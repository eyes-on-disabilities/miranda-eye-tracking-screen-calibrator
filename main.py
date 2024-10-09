import argparse

from data_providers import data_providers
from transformers import transformers
from publishers import publishers
from guis import guis

parser = argparse.ArgumentParser()
parser.add_argument(
    "--data-provider",
    help='The provider of input data. default="%(default)s"',
    choices=data_providers,
    default=next(iter(data_providers)),  # the first mentioned key
)
parser.add_argument(
    "--transformer",
    type=str,
    help=(
        'The transformation technique to transform vectors of the provider to the screen resolution. '
        'default="%(default)s"'
    ),
    choices=transformers,
    default=next(iter(transformers)),  # the first mentioned key
)
parser.add_argument(
    "--publisher",
    help='The method for publishing the resulting vectors. default="%(default)s"',
    choices=publishers,
    default=next(iter(publishers)),  # the first mentioned key
)
parser.add_argument(
    "--gui",
    help='The GUI. default="%(default)s"',
    choices=guis,
    default=next(iter(guis)),  # the first mentioned key
)

args = parser.parse_args()
print(args)
