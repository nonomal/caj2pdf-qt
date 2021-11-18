#!/usr/bin/python

import os
import platform
import subprocess
from shutil import move

# update submodules
workdir = os.getcwd()
os.chdir(workdir)
subprocess.run(["git", "submodule", "update", "--init", "--recursive"])

# build caj2pdf
workdir_caj2pdf = os.path.join(workdir, "caj2pdf")
if os.name != "nt":
    os.chdir(os.path.join(workdir_caj2pdf, "lib"))
    pkg_config_cflags = subprocess.getoutput("pkg-config --cflags jbig2dec")
    pkg_config_libs = subprocess.getoutput("pkg-config --libs jbig2dec").split(" ")
    subprocess.run(["gcc", "-Wall", "-fPIC", "--shared", "-o", "libjbigdec.so", "jbigdec.cc", "JBigDecode.cc"])
    subprocess.run(["gcc", "-Wall", pkg_config_cflags, "-fPIC", "-shared", "-o", "libjbig2codec.so", "decode_jbig2data_x.cc", pkg_config_libs[0], pkg_config_libs[1]])
os.chdir(workdir_caj2pdf)
subprocess.run(["git", "apply", "../caj2pdf.diff"])
subprocess.run(["python", "-m", "venv", "venv"])
subprocess.run(["./venv/bin/python", "-m", "pip", "install", "--index-url=https://mirrors.aliyun.com/pypi/simple", "pypdf2", "pyinstaller"])
subprocess.run(["./venv/bin/pyinstaller", "-F", "caj2pdf"])

# build mupdf
workdir_mupdf = os.path.join(workdir, "mupdf")
os.chdir(workdir_mupdf)
subprocess.run(["make"])

# build project
build_dir = os.path.join(workdir, "build")
build_external_dir = os.path.join(build_dir, "external")
src_dir = os.path.join(workdir, "src")
os.mkdir(build_dir)
os.mkdir(build_external_dir)
move(os.path.join(os.path.join(workdir_caj2pdf, "dist"), "caj2pdf"),
         os.path.join(build_external_dir, "caj2pdf"))
move(os.path.join(os.path.join(os.path.join(workdir_mupdf, "build"), "release"), "mutool"),
         os.path.join(build_external_dir, "mutool"))
os.chdir(src_dir)
subprocess.run(["cmake", "."])
subprocess.run(["cmake", "--build", "."])
os.chdir(build_dir)
if platform.system() == "Darwin":
    move(os.path.join(src_dir, "caj2pdf.app"),
         os.path.join(build_dir, "caj2pdf.app"))
else:
    move(os.path.join(src_dir, "caj2pdf"),
         os.path.join(build_dir, "caj2pdf"))

# clean
os.chdir(workdir_caj2pdf)
subprocess.run(["git", "checkout", "--", "."])
