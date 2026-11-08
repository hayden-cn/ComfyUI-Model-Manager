import os
import time

import folder_paths

from aiohttp import web

from . import utils


def validate_upload_path(file_folder: str, filename: str) -> str:
    """
    Validate upload path to prevent path traversal attacks.
    Returns the safe full path if valid, raises RuntimeError otherwise.
    """
    if not filename or "/" in filename or "\\" in filename:
        raise RuntimeError(f"Invalid filename: {filename}")

    real_folder = os.path.realpath(file_folder)

    allowed_bases = utils.resolve_model_base_paths()
    is_allowed = False
    for _model_type, base_paths in allowed_bases.items():
        for base_path in base_paths:
            real_base = os.path.realpath(base_path)
            if real_folder == real_base or real_folder.startswith(real_base + os.sep):
                is_allowed = True
                break
        if is_allowed:
            break

    if not is_allowed:
        raise RuntimeError(f"Upload folder not in allowed paths: {file_folder}")

    full_path = os.path.realpath(os.path.join(real_folder, filename))
    if not (full_path == real_folder or full_path.startswith(real_folder + os.sep)):
        raise RuntimeError(f"Path traversal detected in filename: {filename}")

    return full_path


class ModelUploader:
    def add_routes(self, routes):

        @routes.get("/model-manager/supported-extensions")
        async def fetch_model_exts(request):
            """
            Get model exts
            """
            try:
                supported_extensions = list(folder_paths.supported_pt_extensions)
                return web.json_response({"success": True, "data": supported_extensions})
            except Exception as e:
                error_msg = f"Get model supported extension failed: {str(e)}"
                utils.print_error(error_msg)
                return web.json_response({"success": False, "error": error_msg})

        @routes.post("/model-manager/upload")
        async def upload_model(request):
            """
            Upload model
            """
            try:
                reader = await request.multipart()
                await self.upload_model(reader)
                utils.print_info(f"Upload model success")
                return web.json_response({"success": True, "data": None})
            except Exception as e:
                error_msg = f"Upload model failed: {str(e)}"
                utils.print_error(error_msg)
                return web.json_response({"success": False, "error": error_msg})

    async def upload_model(self, reader):
        uploaded_size = 0
        last_update_time = time.time()
        interval = 1.0
        file_folder = None

        while True:
            part = await reader.next()
            if part is None:
                break

            name = part.name
            if name == "folder":
                file_folder = await part.text()

            if name == "file":
                if not file_folder:
                    raise RuntimeError("Missing required field: folder")
                filename = part.filename
                filepath = validate_upload_path(file_folder, filename)
                tmp_filepath = filepath + ".tmp"

                with open(tmp_filepath, "wb") as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        f.write(chunk)
                        uploaded_size += len(chunk)

                        if time.time() - last_update_time >= interval:
                            update_upload_progress = {
                                "uploaded_size": uploaded_size,
                            }
                            await utils.send_json("update_upload_progress", update_upload_progress)

        update_upload_progress = {
            "uploaded_size": uploaded_size,
        }
        await utils.send_json("update_upload_progress", update_upload_progress)
        os.rename(tmp_filepath, filepath)
