import torch
import wandb
from baselines.common.registry import registry
from torch.utils.tensorboard import SummaryWriter


class Logger:
    """Generic class to interface with various logging modules, e.g. wandb,
    tensorboard, etc.
    """

    def __init__(self, config):
        self.config = config

    def watch(self, model):
        """
        Monitor parameters and gradients.
        """
        raise NotImplementedError

    def log(self, update_dict, step=None, split=""):
        """
        Log some values.
        """
        assert step is not None
        if split != "":
            new_dict = {}
            for key in update_dict:
                new_dict["{}/{}".format(split, key)] = update_dict[key]
            update_dict = new_dict
        return update_dict


@registry.register_logger("wandb")
class WandBLogger(Logger):
    def __init__(self, config):
        super().__init__(config)
        wandb.init(
            config=self.config,
            id=self.config["cmd"]["timestamp"],
            name=self.config["cmd"]["identifier"],
            dir="logs/wandb",
        )

    def watch(self, model):
        wandb.watch(model)

    def log(self, update_dict, step=None, split=""):
        update_dict = super().log(update_dict, step, split)
        wandb.log(update_dict, step=step)


@registry.register_logger("tensorboard")
class TensorboardLogger(Logger):
    def __init__(self, config):
        super().__init__(config)
        self.writer = SummaryWriter(self.config["cmd"]["logs_dir"])

    def log(self, update_dict, step=None, split=""):
        update_dict = super().log(update_dict, step, split)
        for key in update_dict:
            if torch.is_tensor(update_dict[key]):
                self.writer.add_scalar(key, update_dict[key].val, step)
            else:
                assert isinstance(update_dict[key], int) or isinstance(
                    update_dict[key], float
                )
                self.writer.add_scalar(key, update_dict[key], step)