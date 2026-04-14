"""pytorchexample: A Flower / PyTorch app — Security Experimentation Client."""

import torch
from flwr.app import ArrayRecord, Context, Message, MetricRecord, RecordDict
from flwr.clientapp import ClientApp

from pytorchexample.task import Net, load_data
from pytorchexample.task import test as test_fn
from pytorchexample.task import train_with_attack

# Flower ClientApp
app = ClientApp()


@app.train()
def train(msg: Message, context: Context):
    """Train the model on local data, with optional poisoning attack."""

    # Load the model and initialize it with the received weights
    model = Net()
    model.load_state_dict(msg.content["arrays"].to_torch_state_dict())
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # =========================================================================
    # CONFIGURAÇÃO DINÂMICA DE ATAQUE E HETEROGENEIDADE
    # Estes valores são lidos do pyproject.toml e podem ser sobrescritos
    # via terminal: flwr run . --run-config "poison_rate=0.4 dirichlet_alpha=0.3"
    # =========================================================================
    partition_id = context.node_config["partition-id"]
    num_partitions = context.node_config["num-partitions"]
    batch_size = context.run_config["batch-size"]
    taxa_ataque = context.run_config["poison_rate"]
    dirichlet_alpha = context.run_config["dirichlet_alpha"]
    attack_type = context.run_config.get("attack_type", "label_flipping")

    # Load the data with Dirichlet-based non-IID partitioning
    trainloader, _ = load_data(
        partition_id, num_partitions, batch_size, dirichlet_alpha
    )

    # =========================================================================
    # TREINAMENTO COM ATAQUE DE ENVENENAMENTO
    # =========================================================================
    train_loss, num_poisoned = train_with_attack(
        model,
        trainloader,
        context.run_config["local-epochs"],
        msg.content["config"]["lr"],
        device,
        poison_rate=taxa_ataque,
        attack_type=attack_type,
    )

    is_poisoned = 1.0 if taxa_ataque > 0.0 else 0.0
    print(
        f"[Cliente {partition_id}] loss={train_loss:.4f} | "
        f"ataque={attack_type} | "
        f"amostras_corrompidas={num_poisoned} | "
        f"taxa_ataque={taxa_ataque}"
    )

    # Construct and return reply Message
    model_record = ArrayRecord(model.state_dict())
    metrics = {
        "train_loss": train_loss,
        "num-examples": len(trainloader.dataset),
        "is_poisoned": is_poisoned,
        "num_poisoned_samples": float(num_poisoned),
    }
    metric_record = MetricRecord(metrics)
    content = RecordDict({"arrays": model_record, "metrics": metric_record})
    return Message(content=content, reply_to=msg)


@app.evaluate()
def evaluate(msg: Message, context: Context):
    """Evaluate the model on local data."""

    # Load the model and initialize it with the received weights
    model = Net()
    model.load_state_dict(msg.content["arrays"].to_torch_state_dict())
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Load the data with Dirichlet-based non-IID partitioning
    partition_id = context.node_config["partition-id"]
    num_partitions = context.node_config["num-partitions"]
    batch_size = context.run_config["batch-size"]
    dirichlet_alpha = context.run_config["dirichlet_alpha"]
    _, valloader = load_data(
        partition_id, num_partitions, batch_size, dirichlet_alpha
    )

    # Call the evaluation function
    eval_loss, eval_acc = test_fn(
        model,
        valloader,
        device,
    )

    # Construct and return reply Message
    metrics = {
        "eval_loss": eval_loss,
        "eval_acc": eval_acc,
        "num-examples": len(valloader.dataset),
    }
    metric_record = MetricRecord(metrics)
    content = RecordDict({"metrics": metric_record})
    return Message(content=content, reply_to=msg)
