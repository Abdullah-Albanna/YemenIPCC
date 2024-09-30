from PIL import Image
import base64
import io

from .byte_objects import *

def base64_string_to_image(base64_string):
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes))
    
    return image

def base64_string_to_variable(base64_string):
    image_bytes = base64.b64decode(base64_string)
    image = io.BytesIO(image_bytes)

    return image



class Images:
    email_icon_png = base64_string_to_image(email_icon_png_base64)
    entry_bg_icon_image_1_png = base64_string_to_image(entry_bg_icon_image_1_png_base64)
    entry_bg_icon_image_2_png = base64_string_to_image(entry_bg_icon_image_2_png_base64)
    login_background_png = base64_string_to_image(login_background_png_base64)
    login_button_png = base64_string_to_image(login_button_png_base64)
    login_entry_1_png = base64_string_to_image(login_entry_1_png_base64)
    login_entry_2_png = base64_string_to_image(login_entry_2_png_base64)
    login_hover_button_png = base64_string_to_image(login_hover_button_png_base64)
    login_signup_button_png = base64_string_to_image(login_signup_button_png_base64)
    login_signup_hover_button_png = base64_string_to_image(login_signup_hover_button_png_base64)
    password_icon_png = base64_string_to_image(password_icon_png_base64)
    signup_background_png = base64_string_to_image(signup_background_png_base64)
    signup_button_png = base64_string_to_image(signup_button_png_base64)
    signup_entry_1_bg_icon_png = base64_string_to_image(signup_entry_1_bg_icon_png_base64)
    signup_entry_1_png = base64_string_to_image(signup_entry_1_png_base64)
    signup_entry_2_bg_icon_png = base64_string_to_image(signup_entry_2_bg_icon_png_base64)
    signup_entry_2_png = base64_string_to_image(signup_entry_2_png_base64)
    signup_entry_3_bg_icon_png = base64_string_to_image(signup_entry_3_bg_icon_png_base64)
    signup_entry_3_png = base64_string_to_image(signup_entry_3_png_base64)
    signup_hover_button_png = base64_string_to_image(signup_hover_button_png_base64)
    signup_login_button_png = base64_string_to_image(signup_login_button_png_base64)
    signup_login_hover_button_png = base64_string_to_image(signup_login_hover_button_png_base64)
    username_icon_png = base64_string_to_image(username_icon_png_base64)
    loading_gif = base64_string_to_image(loading_gif_base64)
    loading_gif = base64_string_to_variable(loading_gif_base64)
    loadingd_gif = base64_string_to_image(loadingd_gif_base64)
    background_png = base64_string_to_image(background_png_base64)
    YemenIPCC_ico = base64_string_to_image(YemenIPCC_ico_base64)
    YemenIPCC_icns = base64_string_to_image(YemenIPCC_icns_base64)
    YemenIPCC_png = base64_string_to_image(YemenIPCC_png_base64)