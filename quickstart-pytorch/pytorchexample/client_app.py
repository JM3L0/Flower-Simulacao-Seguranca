"""pytorchexample: A Flower / PyTorch app — Security Experimentation Client."""

import torch
from flwr.app import ArrayRecord, Context, Message, MetricRecord, RecordDict
from flwr.clientapp import ClientApp

from pytorchexample.task import Net, load_data, train_with_attack
from pytorchexample.task import test as test_fn

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
    seed = context.run_config.get("seed", 42)

    # Load the data with Dirichlet-based non-IID partitioning
    trainloader, _ = load_data(
        partition_id, num_partitions, batch_size, dirichlet_alpha, seed=seed
    )


    # Determina se este nó é atacante de acordo com a fração Bizantina
    num_atacantes = int(num_partitions * taxa_ataque)
    is_malicious = partition_id < num_atacantes

    # =========================================================================
    # TREINAMENTO COM CONTROLE BIZANTINO
    # =========================================================================
    train_loss, num_poisoned = train_with_attack(
        model,
        trainloader,
        context.run_config["local-epochs"],
        msg.content["config"]["lr"],
        device,
        poison_rate=1.0 if is_malicious else 0.0,
        attack_type=attack_type,
        is_malicious=is_malicious,
    )

    status_str = f"MALICIOSO ({attack_type})" if is_malicious else "HONESTO"
    print(
        f"[Cliente {partition_id:02d} - {status_str}] loss={train_loss:.4f} | "
        f"amostras_corrompidas={num_poisoned}"
    )

    is_poisoned = 1.0 if is_malicious else 0.0

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
