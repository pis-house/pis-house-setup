import subprocess

class Esp32FileTransfer:
    ESP32_PORT = '/dev/ttyUSB0'
    ESP32_CHIP = 'esp32'
    # Huge APP (3MB No OTA/1MB SPIFFS) の構成
    # アプリ領域(0x300000) + オフセット(0x10000) = 0x310000 が開始位置
    LITTLEFS_START_ADDR = '0x310000' 
    # サイズは表記上1MBですが、4MBフラッシュに収めるため実質 0xE0000 (896KB) です
    # ※もし書き込みエラーが出る場合は 0xD0000 など少し減らして試してください
    LITTLEFS_SIZE = '0xE0000'
    
    @staticmethod
    def image_create_and_upload(data_folder, mklittlefs_path, output_image):
        mklittlefs_command = [
            mklittlefs_path,
            '-c', data_folder,
            '-s', Esp32FileTransfer.LITTLEFS_SIZE,
            '-p', '256',
            '-b', '4096',
            '-d', '5',
            output_image
        ]
        try:
            subprocess.run(
                mklittlefs_command,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            return f"\nLittleFSイメージの生成に失敗しました!\nエラー詳細: {e.stderr}"
        except FileNotFoundError:
            return f"\n{mklittlefs_command[0]}が見つかりません。パスを確認してください。"

        esptool_command = [
            'esptool.py',
            '--chip', Esp32FileTransfer.ESP32_CHIP,
            '--port', Esp32FileTransfer.ESP32_PORT,
            'write_flash',
            '-fm', 'dio',
            Esp32FileTransfer.LITTLEFS_START_ADDR,
            output_image
        ]
        try:
            subprocess.run(
                esptool_command,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            return f"\nフラッシュへの書き込みに失敗しました!\nエラー詳細: {e.stderr}"
        except FileNotFoundError:
            return f"\n{esptool_command[0]}が見つかりません。パスを確認してください。"


        return None
