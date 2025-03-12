# Initialize colorama for Windows
from colorama import Fore, Style
import shutil
# ASCII art banner
BANNER = fr"""
       {Fore.GREEN}.{Fore.WHITE}                      {Fore.GREEN}.{Fore.WHITE}                     {Fore.GREEN}.{Fore.WHITE}                         {Fore.GREEN}.{Fore.WHITE}                   
__________________ {Fore.GREEN}°{Fore.WHITE} _          _   _           _              ______   {Fore.GREEN}.{Fore.WHITE}  _        _                    
| ___ \  _  \ {Fore.GREEN}.{Fore.WHITE}___| | |   {Fore.GREEN}°{Fore.WHITE}    | | | |{Fore.GREEN}.{Fore.WHITE} {Fore.GREEN}o{Fore.WHITE}   {Fore.GREEN}.{Fore.WHITE}  | |  {Fore.GREEN}.{Fore.WHITE} {Fore.GREEN}0{Fore.WHITE}   {Fore.GREEN}o{Fore.WHITE}    |  _ {Fore.GREEN}.{Fore.WHITE}\    | |   {Fore.GREEN}.{Fore.WHITE}  |{Fore.GREEN}°{Fore.WHITE}|   {Fore.GREEN}°.{Fore.WHITE}   {Fore.GREEN}o.{Fore.WHITE}    {Fore.GREEN}0{Fore.WHITE}   
| |_/ /{Fore.GREEN}.{Fore.WHITE}| | | |_    | |_ ___ {Fore.GREEN}.{Fore.WHITE} | | | | ___{Fore.GREEN}°{Fore.WHITE} ___| |_ ___. _ __ {Fore.GREEN}°{Fore.WHITE}| | | |__ _| |_ __{Fore.GREEN}°{Fore.WHITE}_| |__ {Fore.GREEN}0{Fore.WHITE} __ _{Fore.GREEN}°{Fore.WHITE}___ {Fore.GREEN}°{Fore.WHITE}___ 
|{Fore.GREEN}°{Fore.WHITE} __/| | | |{Fore.GREEN}°{Fore.WHITE} _|   | __/ _ \  | | | |/ _ \/ __| __/ _ \| '__| | | | / _` |{Fore.GREEN}.{Fore.WHITE}__/ _` | '_ \ / _` / __|/ _ \ 
| | {Fore.GREEN}.{Fore.WHITE} | |/ /| |   {Fore.GREEN}0{Fore.WHITE} | || (_) | \ \_/ / {Fore.GREEN}°{Fore.WHITE}__/ (__| || (_) |{Fore.GREEN}°{Fore.WHITE}|   {Fore.GREEN}.{Fore.WHITE}| |/ / (_| | || (_| | |_) | (_| \__ \  __/
\_|{Fore.GREEN}0{Fore.WHITE}  |___/ \_| {Fore.GREEN}°{Fore.WHITE} {Fore.GREEN}.{Fore.WHITE}  \__\___/ {Fore.GREEN}0{Fore.WHITE} \___/ \___|\___|\__\___/|_|  {Fore.GREEN}0{Fore.WHITE} |___/ \__,_|\__\__,_|_{Fore.GREEN}.{Fore.WHITE}__/ \__,_|___/\___|                  
  {Fore.YELLOW}*{Fore.RED}   )           )      {Fore.YELLOW}°{Fore.RED}            (    (  (     {Fore.YELLOW}*{Fore.RED}   )           )  {Fore.YELLOW}°{Fore.RED}                (    (    )
{Fore.YELLOW}`{Fore.RED} )  /(  ( {Fore.YELLOW}*{Fore.RED}   ( /((   (    (  (  {Fore.YELLOW}°{Fore.RED}   )\   )\ )\  {Fore.YELLOW}`{Fore.RED} )  /(  (  {Fore.YELLOW}*{Fore.RED}  ( /((     {Fore.YELLOW}*{Fore.RED}  (  (    {Fore.YELLOW}°{Fore.RED} )\   )\   )(  )
 ( )({Fore.YELLOW}_{Fore.RED}))))\(   )\())\  )) {Fore.YELLOW}*{Fore.RED} )\))(  (((({Fore.YELLOW}_{Fore.RED})((({Fore.YELLOW}_{Fore.RED})({Fore.YELLOW}_{Fore.RED})  ( )({Fore.YELLOW}_{Fore.RED}))))\(   )\())\  (    )\))(  (((({Fore.YELLOW}_{Fore.RED})((({Fore.YELLOW}_{Fore.RED}) (({Fore.YELLOW}_{Fore.RED})({Fore.YELLOW}_{Fore.RED}))
{Fore.WHITE}##########################################################################################################
"""

def display_banner():
    # Display welcome banner with ASCII art
    print(BANNER + Style.BRIGHT)
    print("Welcome to PDF to Vector Database Converter" + Style.NORMAL)
    print("------------------------------------------" + Style.DIM)


def get_terminal_size():
# Get terminal size, return (0, 0) if can't determine
    try:
        columns, rows = shutil.get_terminal_size()
        return columns, rows
    except:
        return 0, 0

def display_banner():
    columns, rows = get_terminal_size()
    
    # Check if terminal is large enough for ASCII art banner (width > 100, height > 15)
    if columns >= 110 and rows >= 20:
        print(BANNER + Style.BRIGHT)
    else:
        # Fallback to simple text banner if terminal is too small
        print(f"\n{Fore.CYAN}{'='*20}")
        print(f"{Fore.WHITE}PDF to Vector DB")
        print(f"Version 1.0.0")
        print(f"{Fore.CYAN}{'='*20}{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}Welcome to PDF to Vector Database Converter{Style.RESET_ALL}")
    print(f"{Fore.WHITE}------------------------------------------{Style.RESET_ALL}")