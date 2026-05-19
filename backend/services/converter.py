import os
import subprocess


def convert_file(input_path: str, output_format: str,
                 quality: str = "medium") -> dict:
    input_ext = input_path.rsplit('.', 1)[-1]
    base_name = input_path.rsplit('.', 1)[0]
    output_path = f"{base_name}.{output_format}"

    quality_map = {
        'high': ['-crf', '18'],
        'medium': ['-crf', '23'],
        'low': ['-crf', '30'],
    }

    cmd = ['ffmpeg', '-y', '-i', input_path]

    if output_format in ('mp4', 'webm', 'mkv'):
        cmd += quality_map.get(quality, quality_map['medium'])
        cmd += ['-c:a', 'aac', '-b:a', '192k']
    elif output_format == 'mp3':
        cmd += ['-vn', '-ab', '192k', '-ar', '44100']
    elif output_format == 'aac':
        cmd += ['-vn', '-c:a', 'aac', '-b:a', '256k']
    elif output_format == 'flac':
        cmd += ['-vn', '-c:a', 'flac']
    elif output_format == 'wav':
        cmd += ['-vn', '-c:a', 'pcm_s16le']

    cmd.append(output_path)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    _, stderr = process.communicate(timeout=3600)

    if process.returncode == 0:
        file_size = (
            os.path.getsize(output_path)
            if os.path.exists(output_path) else 0
        )
        return {
            "success": True,
            "output_path": output_path,
            "file_size": file_size,
        }
    else:
        return {
            "success": False,
            "error": (stderr[-500:] if stderr else "转换失败"),
        }
