from pprint import pprint
import subprocess
import urllib.request as request

def print_object(slic3r_path, in_filename, out_filename, part_url, quantity, material, layer_height, infill, perimeters, top_and_bottom_layers):
    cmd = f"{slic3r_path} -o {out_filename} --duplicate {quantity} --layer-height {layer_height} " + \
        f"--fill-density {infill} --perimeters {perimeters} --top-solid-layers {top_and_bottom_layers} --bottom-solid-layers {top_and_bottom_layers} " + \
        f"--fill-pattern gyroid --skirts 0 --gui {in_filename}"
    return subprocess.call(cmd, shell=True)

def download_file(url, filename):
    print('Downloading: ' + url)
    data = request.urlopen(url).read()
    with open(f'./{filename}', 'wb') as f:  
        f.write(data)

def fetch_instructions_and_parts(branch, frame, printer, slic3r_path):
    base_url = f"https://cdn.jsdelivr.net/gh/hairychris/prusa_i3_bear_upgrade@{branch}/{frame}_upgrade/for_{printer}/"
    instructions_url = base_url + "manual/print_settings.md"
    parts_url = base_url + "printed_parts/stl/"
    print('Downloading instructions from: ' + instructions_url)
    response = request.urlopen(instructions_url).read().decode('utf8').split("\n")
    output = []
    for count, line in enumerate(response):
        if line.startswith('| '):
            split_line = line.split('|')
            no_space_line = []
            for col in split_line:
                no_space_line.append(col.strip().replace('<br/>', ' ').split(' (')[0])
            if count > 18:
                output_dict = {
                    'slic3r_path': slic3r_path,
                    'in_filename': f'{no_space_line[1]}.stl',
                    'out_filename': f'{no_space_line[1]}.gcode',
                    'part_url': f'{parts_url}{no_space_line[1]}.stl',
                    'quantity': no_space_line[2],
                    'material': no_space_line[3],
                    'layer_height': no_space_line[4][:-2],
                    'infill': no_space_line[5],
                    'perimeters': no_space_line[6],
                    'top_and_bottom_layers': no_space_line[7]
                }
                pprint(output_dict)
                download_file(output_dict['part_url'], output_dict['in_filename'])
                result = print_object(**output_dict)
                output.append({'instructions': output_dict, 'result': result})
                print(result)
    return output

print('We just need to ask a few questions, hit enter to accept the shown default value.')
branch = input("What github version do you want to use? [master]: ") or "master"
frame = input("What style frame do you have? [full]: ") or "full"
printer = input("What model of printer do you have? [mk3]: ") or "mk3"
slic3r_path = input("Where is Slic3r PE installed? [/Applications/Slic3r.app/Contents/MacOS/Slic3r]: ") or "/Applications/Slic3r.app/Contents/MacOS/Slic3r"
fetch_instructions_and_parts(branch, frame, printer, slic3r_path)

# curl -fsS https://raw.githubusercontent.com/gregsaun/prusa_i3_bear_upgrade/master/slice_now.py | python3