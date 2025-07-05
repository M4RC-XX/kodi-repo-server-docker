#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Kodi Repo Generator for Python 3 - Copyright (c) 2024 Loki1979 - Created on 10.02.2024 08:45

import os
import sys
import re
import zipfile
import hashlib
import xml.etree.ElementTree as ET
import gzip
from shutil import copy2, rmtree

def print_to_stdout(message):
	sys.stdout.buffer.write(message.encode("UTF-8"))
	sys.stdout.flush()

def calculate_hash(file_path, algorithm="sha256"):
	hash_func = hashlib.new(algorithm)
	with open(file_path, 'rb') as file:
		for chunk in iter(lambda: file.read(8192), b''):
			hash_func.update(chunk)
	return hash_func.hexdigest()

def compress_file(file_path):
	with open(file_path, 'rb') as f_in:
		with gzip.open(file_path + '.gz', 'wb') as f_out:
			f_out.writelines(f_in)

def create_new_repo(addons_dir, new_repo_dir, hash_algorithm="sha256"):
	print_to_stdout("Kodi Repo Generator for Python 3 - Copyright (c) 2024 Loki1979 - Created on 10.02.2024 08:45\n")
	print_to_stdout(f"Python Version: {sys.version}\n\n")
	print_to_stdout("Starting Repo Generator!\n\n")

	os.makedirs(addons_dir, exist_ok=True)

	if os.path.exists(new_repo_dir):
		rmtree(new_repo_dir, ignore_errors=True)

	print_to_stdout(f"Addons directory:\n{addons_dir}\n\n")
	print_to_stdout(f"Repo directory:\n{new_repo_dir}\n\n")
	print_to_stdout(f"Processing addons and creating a new repo structure under:\n{new_repo_dir}\n\n")

	addon_counter = 0
	addons_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n\n"
	addons_error_log = ""

	for addon in os.listdir(addons_dir):
		if (re.search(r"(context|metadata|plugin|inputstream|repo|resource|script|service|skin|weather|slyguy)", addon) and os.path.isdir(os.path.join(addons_dir, addon))):
			try:
				addon_xml_path = os.path.join(addons_dir, addon, "addon.xml")
				if os.path.exists(addon_xml_path):

					name = ""
					id = ""
					version = ""
					provider = ""
					xml_image_paths = []
					for elem in ET.parse(addon_xml_path).getroot().iter():

						if elem.tag == "addon":
							name = re.sub(r"\[[^\]]*\]", "", elem.attrib['name'])
							id = elem.attrib['id']
							version = "-" + elem.attrib['version']
							provider = re.sub(r"\[[^\]]*\]", "", elem.attrib['provider-name'])
							print_to_stdout(f"Addon Name       : {name}\nAddon ID         : {id}\nAddon Ver        : {version[1:]}\nAuthor           : {provider}\n")

						if elem.tag in {"icon", "fanart", "banner", "clearlogo", "screenshot"}:
							if elem.text:
								xml_image_path = os.path.normpath(elem.text)
								if xml_image_path not in xml_image_paths:
									xml_image_paths.append(xml_image_path)

					if not addon == id:
						print_to_stdout(f"Name Correction  : {addon} = {id}\n")

					os.makedirs(os.path.join(new_repo_dir, id), exist_ok=True)
					print_to_stdout(f"Folder created   : {id}\n")

					for file in os.listdir(os.path.join(addons_dir, addon)):
						if (re.search(r"(addon.xml|changelog.txt)", file)) or (
								re.search(r"(icon|fanart)", file) and re.search(r"(.png|.jpg|.jpeg|.bmp|.gif)", file)):
							copy2(os.path.join(addons_dir, addon, file),
									os.path.join(new_repo_dir, id, file))
							print_to_stdout(f"File copied      : {file}\n")

					files_list = list(os.walk(os.path.join(addons_dir, addon), topdown=False, onerror=None, followlinks=True))
					list_len = sum(len(files) for _, _, files in files_list)
					zip_file_path = os.path.join(new_repo_dir, id, f"{id}{version}.zip")

					with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip:
						rootlen = len(os.path.join(addons_dir, addon)) + 1
						counter = 0

						for root, _, files in files_list:
							for file in files:
								if not(re.search(r"(__pycache__|venv)", root)and not re.search(r"(.git|.bak|.idea|.gitignore|.gitattributes|.DS_Store)", file)):
									file_path = os.path.join(root, file)
									zip.write(file_path, os.path.join(id, file_path[rootlen:]))

								counter += 1
								percent = ("{0:.0f}").format(100 * (counter / float(list_len)))
								filled_length = int(50 * counter / list_len)
								bar = "█" * filled_length + '-' * (50 - filled_length)
								print_to_stdout(f"\rCreating Zip     : {bar}| {percent}%\r")

								if counter == list_len:
									print_to_stdout("\n")

					print_to_stdout(f"Zip created      : {id}{version}.zip\n")

					zip_hash_path = os.path.join(new_repo_dir, id, f"{id}{version}.zip.{hash_algorithm}")
					with open(zip_hash_path, "wb") as hash_file:
						hash_file.write(f"{calculate_hash(zip_file_path, hash_algorithm)}  {id}{version}.zip".encode("UTF-8"))
					print_to_stdout(f"{hash_algorithm} created   : {id}{version}.zip.{hash_algorithm}\n")

					if xml_image_paths:
						for image_path in xml_image_paths:
							if (os.path.exists(os.path.join(addons_dir,addon,image_path)) and not os.path.exists(os.path.dirname(os.path.join(new_repo_dir,id,image_path)))):
								os.makedirs(os.path.dirname(os.path.join(new_repo_dir,id,image_path)))
								print_to_stdout(f"Folder created   : {id}/{os.path.dirname(image_path)}\n")
							if (os.path.exists(os.path.join(addons_dir,addon,image_path)) and not os.path.exists(os.path.join(new_repo_dir,id,image_path))):
								copy2(os.path.join(addons_dir,addon,image_path),os.path.join(new_repo_dir,id,image_path))
								print_to_stdout(f"File copied      : {os.path.basename(image_path)}\n")
					else:print_to_stdout("No display image : No XML image paths found!\n\n")

					with open(addon_xml_path,"r",encoding="UTF-8") as xml:
						addon_xml_content = "".join(line.rstrip() + "\n" for line in xml.readlines() if not (line.find("<?xml") >= 0))

					addons_xml += f"{addon_xml_content.strip()}\n\n"
					print_to_stdout("\n")
					addon_counter += 1

			except Exception as e:
				addons_error_log += f"Addon Name       : {addon}\nError            : {e}\n\n"

	if addon_counter > 0:
		try:
			addons_xml = f"{addons_xml.strip()}\n\n</addons>".encode("UTF-8")
			with open(os.path.join(new_repo_dir, "addons.xml"), "wb") as fi:
				fi.write(addons_xml)
		except Exception as e:
			print_to_stdout(f"The file (addons.xml) could not be created!\n{e}")
			sys.exit()

		try:
			addons_xml_hash = calculate_hash(os.path.join(new_repo_dir, "addons.xml"), hash_algorithm)
			with open(os.path.join(new_repo_dir, f"addons.xml.{hash_algorithm}"), "wb") as fi:
				fi.write(f"{addons_xml_hash}  addons.xml".encode("UTF-8"))
		except Exception as e:
			print_to_stdout(f"The file (addons.xml.{hash_algorithm}) could not be created!\n{e}")
			sys.exit()

		# Komprimiere addons.xml
		compress_file(os.path.join(new_repo_dir, "addons.xml"))

		# Berechne den Hash für die komprimierte Datei
		addons_xml_gz_hash = calculate_hash(os.path.join(new_repo_dir, "addons.xml.gz"), hash_algorithm)

		# Speichere den Hash-Wert
		with open(os.path.join(new_repo_dir, f"addons.xml.gz.{hash_algorithm}"), "wb") as fi:
			fi.write(f"{addons_xml_gz_hash}  addons.xml.gz".encode("UTF-8"))

		print_to_stdout(f"Addons in Repo   : {addon_counter}\n")
		print_to_stdout(f"File created     : addons.xml\n")
		print_to_stdout(f"File created     : addons.xml.{hash_algorithm}\n")
		print_to_stdout(f"File created     : addons.xml.gz\n")
		print_to_stdout(f"File created     : addons.xml.gz.{hash_algorithm}\n")
		print_to_stdout("Finished!\n\n")

		if addons_error_log:
			print_to_stdout(f"Error Report     :\n\n{addons_error_log}")
	else:
		print_to_stdout(f"No addons in addons directory:\n{addons_dir}\n\n")

if __name__ == "__main__":
    # Überprüfe, ob die Pfade als Kommandozeilenargumente übergeben wurden
    if len(sys.argv) != 3:
        print("Usage: python generator.py <path_to_addons_directory> <path_to_new_repo_directory>")
        sys.exit(1)

    addons_dir = os.path.normpath(sys.argv[1])
    new_repo_dir = os.path.normpath(sys.argv[2])
    hash_algorithm = "sha256"
    
    # Rufe die Hauptfunktion mit den übergebenen Pfaden auf
    create_new_repo(addons_dir, new_repo_dir, hash_algorithm)