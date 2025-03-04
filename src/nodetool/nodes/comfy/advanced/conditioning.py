from pydantic import Field
from nodetool.metadata.types import CLIP, Conditioning
from nodetool.common.comfy_node import ComfyNode


class CLIPTextEncodeSDXLRefiner(ComfyNode):
    """
    Encodes text using CLIP for the SDXL refiner model.
    clip, text, encode, sdxl, refiner

    Use cases:
    - Prepare text prompts for SDXL refiner model
    - Incorporate aesthetic scores in text encoding
    - Generate conditionings for high-resolution image refinement
    """

    ascore: float = Field(default=6.0, description="The ascore to use.")
    width: int = Field(default=1024, le=2048, description="The width to use.")
    height: int = Field(default=1024, le=2048, description="The height to use.")
    text: str = Field(default="", description="The text to encode.")
    clip: CLIP = Field(default=CLIP(), description="The CLIP to use.")

    @classmethod
    def return_type(cls):
        return {"conditioning": Conditioning}


class CLIPTextEncodeSDXL(ComfyNode):
    """
    Encodes text using CLIP for the base SDXL model.
    clip, text, encode, sdxl, base

    Use cases:
    - Prepare text prompts for base SDXL model
    - Handle separate global and local text prompts
    - Generate conditionings with specific crop and target dimensions
    """

    width: int = Field(default=1024, le=2048, description="The width to use.")
    height: int = Field(default=1024, le=2048, description="The height to use.")
    crop_w: int = Field(default=0, le=2048, description="The crop width to use.")
    crop_h: int = Field(default=0, le=2048, description="The crop height to use.")
    target_width: int = Field(
        default=1024, le=2048, description="The target width to use."
    )
    target_height: int = Field(
        default=1024, le=2048, description="The target height to use."
    )
    text_g: str = Field(
        default="CLIP_G",
        description="The global text to encode.",
    )
    text_l: str = Field(
        default="CLIP_L",
        description="The local text to encode.",
    )
    clip: CLIP = Field(default=CLIP(), description="The CLIP to use.")

    @classmethod
    def return_type(cls):
        return {"conditioning": Conditioning}
