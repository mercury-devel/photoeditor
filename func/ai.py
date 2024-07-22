import aiohttp
import aiofiles
import requests
from os import path
import random
from config import AI_GEN_API, IMGBBTOKEN
from base64 import b64encode

def upload_image_to_imgbb(image_path):
    url = "https://api.imgbb.com/1/upload"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'key': IMGBBTOKEN,
        'image': b64encode(open(image_path, 'rb').read()),
        'expiration': 20
    }
    response = requests.post(url, headers=headers, data=payload)
    json_response = response.json()
    return json_response['data']['url']


async def gen_photo(prompt):
    headers = {
        "Authorization": f"Key {AI_GEN_API}",
        "Content-Type": "application/json"
    }
    data = {
        "model_name": "stabilityai/stable-diffusion-xl-base-1.0",
        "prompt": prompt,
        "negative_prompt": "(worst quality, poor details:1.4), lowres, (artist name, signature, watermark:1.4), bad-artist-anime, bad_prompt_version2, bad-hands-5, ng_deepnegative_v1_75t",
        "guidance_scale": 7.5,
        "controlnet_conditioning_scale": 1,
        "control_guidance_start": 0,
        "control_guidance_end": 1,
        "seed": random.randint(1, 99999),
        "scheduler": "Euler",
        "num_inference_steps": 40,
        "image_size": "landscape_4_3",
        "image_format": "jpeg"
    }
    url = "https://110602490-lora.gateway.alpha.fal.ai"
    session = aiohttp.ClientSession(headers=headers)
    response = await session.post(url=url, json=data)
    json_data = await response.json()
    await session.close()
    return json_data['images'][0]['url']

async def gen_illusion(url, prompt):
    headers = {
        "Authorization": f"Key {AI_GEN_API}",
        "Content-Type": "application/json"
    }
    data = {
        "model_name": "stabilityai/stable-diffusion-xl-base-1.0",
        "prompt": prompt,
        "image_url": url,
        "negative_prompt": "(worst quality, poor details:1.4), lowres, (artist name, signature, watermark:1.4), bad-artist-anime, bad_prompt_version2, bad-hands-5, ng_deepnegative_v1_75t",
        "guidance_scale": 7.5,
        "controlnet_conditioning_scale": 1,
        "control_guidance_start": 0,
        "control_guidance_end": 1,
        "seed": random.randint(1, 99999),
        "scheduler": "Euler",
        "num_inference_steps": 40,
        "image_size": "landscape_4_3",
        "image_format": "jpeg"
    }
    url = "https://54285744-illusion-diffusion.gateway.alpha.fal.ai"
    session = aiohttp.ClientSession(headers=headers)
    response = await session.post(url=url, json=data)
    json_data = await response.json()
    await session.close()
    return json_data['image']['url']

async def cut_photo(url, user_id):
    headers = {
        "Authorization": f"Key {AI_GEN_API}",
        "Content-Type": "application/json"
    }
    data = {
        "image_url": url,
    }
    url = "https://110602490-imageutils.gateway.alpha.fal.ai/rembg"
    session = aiohttp.ClientSession(headers=headers)
    response = await session.post(url=url, json=data)
    json_data = await response.json()
    f_path = f"photos/{user_id}.png"
    async with session.get(json_data['image']['url']) as resp:
        f = await aiofiles.open(f_path, mode='wb')
        await f.write(await resp.read())
        await f.close()

    await session.close()
    return f_path
