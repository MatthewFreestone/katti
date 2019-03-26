import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--zsh", help="install zsh completions", action="store_true")
args = parser.parse_args()

print("\n********************************************************************************\n")
print("""\
\033[1;32m::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:'\033[1;34m##\033[1;32m:::'\033[1;34m##\033[1;32m:::::::'\033[1;34m###\033[1;32m:::::::'\033[1;34m########\033[1;32m::::'\033[1;34m########\033[1;32m::::'\033[1;34m####\033[1;32m:
: \033[1;34m##\033[1;32m::'\033[1;34m##\033[1;32m:::::::'\033[1;34m## ##\033[1;32m::::::... \033[1;34m##\033[1;32m..:::::... \033[1;34m##\033[1;32m..:::::. \033[1;34m##\033[1;32m::
: \033[1;34m##\033[1;32m:'\033[1;34m##\033[1;32m:::::::'\033[1;34m##\033[1;32m:. \033[1;34m##\033[1;32m:::::::: \033[1;34m##\033[1;32m:::::::::: \033[1;34m##\033[1;32m:::::::: \033[1;34m##\033[1;32m::
: \033[1;34m#####\033[1;32m:::::::'\033[1;34m##\033[1;32m:::. \033[1;34m##\033[1;32m::::::: \033[1;34m##\033[1;32m:::::::::: \033[1;34m##\033[1;32m:::::::: \033[1;34m##\033[1;32m::
: \033[1;34m##\033[1;32m. \033[1;34m##\033[1;32m:::::: \033[1;34m#########\033[1;32m::::::: \033[1;34m##\033[1;32m:::::::::: \033[1;34m##\033[1;32m:::::::: \033[1;34m##\033[1;32m::
: \033[1;34m##\033[1;32m:. \033[1;34m##\033[1;32m::::: \033[1;34m##\033[1;32m.... \033[1;34m##\033[1;32m::::::: \033[1;34m##\033[1;32m:::::::::: \033[1;34m##\033[1;32m:::::::: \033[1;34m##\033[1;32m::
: \033[1;34m##\033[1;32m::. \033[1;34m##\033[1;32m:::: \033[1;34m##\033[1;32m:::: \033[1;34m##\033[1;32m::::::: \033[1;34m##\033[1;32m:::::::::: \033[1;34m##\033[1;32m:::::::'\033[1;34m####\033[1;32m:
:.::::..:::::..:::::..::::::::..:::::::::::..::::::::....:::\033[0m\n\
""")
print("\033[1;34m=> \033[1;32mMaking katti directory in /usr/local/opt...\033[0m")
os.system("mkdir -v /usr/local/opt/katti")
print("\033[1;34m=> \033[1;32mMoving files to /usr/local/opt/katti...\033[0m")
os.system("cp -v katti.py /usr/local/opt/katti")
os.system("cp -v latex_to_text.py /usr/local/opt/katti")
print("\033[1;34m=> \033[1;32mMaking katti shell script in /usr/local/bin...\033[0m")
print("echo 'python3 /usr/local/opt/katti/katti.py \"$@\"' > /usr/local/bin/katti")
os.system("echo 'python3 /usr/local/opt/katti/katti.py \"$@\"' > /usr/local/bin/katti")
print("chmod +x /usr/local/bin/katti")
os.system("chmod +x /usr/local/bin/katti")
print("\033[1;34m=> \033[1;32mMaking katti config directory in /usr/local/etc...\033[0m")
os.system("mkdir -v /usr/local/etc/katti")
print("\033[1;34m=> \033[1;32mMoving katti config files to /usr/local/etc/katti...\033[0m")
os.system("cp -v problem_ids.json /usr/local/etc/katti")
print("\033[1;34m=> \033[1;32mInstalling requirements...\033[0m")
os.system("pip3 install -r requirements.txt")

if args.zsh:
  print("\033[1;34m=> \033[1;32mMaking ZSH completions directory in $HOME/.zsh-completions...\033[0m")
  os.system("mkdir -v $HOME/.zsh-completions")
  print("\033[1;34m=> \033[1;32mMoving ZSH compdef files to $HOME/.zsh-completions...\033[0m")
  os.system("cp -v _katti $HOME/.zsh-completions")
  print("\033[1;34m=> \033[1;32mEnsuring $HOME/.zsh-completions is included in $fpath environment variable...\033[0m")
  print("echo 'fpath=($HOME/.zsh-completions $fpath)' >> $HOME/.zshrc")
  os.system("echo 'fpath=($HOME/.zsh-completions $fpath)' >> $HOME/.zshrc")
  print("\033[1;34m=> \033[1;32mRestarting shell session...\033[0m")
  os.system("exec zsh")
print("\n********************************************************************************\n")
