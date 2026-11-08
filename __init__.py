import folder_paths


# NOTE: This is an experiment
# Add .gguf extension to supported_pt_extensions
folder_paths.supported_pt_extensions.add(".gguf")


import os
from .py import config
from .py import utils


extension_uri = utils.normalize_path(os.path.dirname(__file__))

# Init config settings
config.extension_uri = extension_uri

# Try to download web distribution
version = utils.get_current_version()
utils.download_web_distribution(version)


# Add api routes
from .py import manager
from .py import download
from .py import information
from .py import upload

routes = config.routes

manager.ModelManager().add_routes(routes)
download.ModelDownload().add_routes(routes)
information.Information().add_routes(routes)
upload.ModelUploader().add_routes(routes)


WEB_DIRECTORY = "web"
NODE_CLASS_MAPPINGS = {}
__all__ = ["WEB_DIRECTORY", "NODE_CLASS_MAPPINGS"]
