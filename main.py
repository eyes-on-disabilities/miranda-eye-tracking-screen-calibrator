import argparse

from data_providers import data_providers
from guis import guis
from publishers import publishers
from transformers import transformers

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
        "The transformation technique to transform vectors of the provider to the screen resolution. "
        'default="%(default)s"'
    ),
    choices=transformers,
    default=next(iter(transformers)),
)
parser.add_argument(
    "--publisher",
    help='The method for publishing the resulting vectors. default="%(default)s"',
    choices=publishers,
    default=next(iter(publishers)),
)
parser.add_argument(
    "--gui",
    help='The GUI. default="%(default)s"',
    choices=guis,
    default=next(iter(guis)),
)

args = parser.parse_args()

data_provider = data_providers[args.data_provider]()
transformer = transformers[args.transformer]()
publisher = publishers[args.publisher]()
gui = guis[args.gui]()

