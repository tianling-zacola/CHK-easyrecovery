import os
import shutil
import zipfile

class FileRecoveryEngine:
    def __init__(self, config_file=None):
        """初始化恢复引擎，加载内外规则"""
        # 内置文件签名规则（优先级较低）
        self.internal_signatures = [
            (b'MZ', '.exe'),
            (b'\x7F\x45\x4C\x46', '.elf'),
            (b'\xD0\xCF\x11\xE0', '_ms_office_old'),
            (b'PK\x03\x04', '_zip_analyze'),
            (b'%PDF-', '.pdf'),
            (b'\x52\x61\x72\x21', '.rar'),
            (b'\xDB\xA5\x2D\x00', '.wps'), # WPS文档
            (b'\x31\xBE\x00\x00', '.wri'), # Windows Write文档
        
        # 图片
            (b'\xFF\xD8\xFF', '.jpg'),     # JPEG
            (b'\x89\x50\x4E\x47', '.png'), # PNG
            (b'GIF', '.gif'),              # GIF 
            (b'\x42\x4D', '.bmp'),         # BMP
            (b'\x49\x49\x2A\x00', '.tif'), # TIFF (小端)
            (b'\x4D\x4D\x00\x2A', '.tif'), # TIFF (大端)
            (b'\x00\x00\x01\x00', '.ico'), # ICO图标
            (b'\x38\x42\x50\x53', '.psd'), # Photoshop
        
        # 音频
            (b'ID3', '.mp3'),              # MP3
            (b'\xFF\xFB', '.mp3'),         # MP3 without ID3
            (b'RIFF', '.wav'),             # WAV
            (b'OggS', '.ogg'),             # OGG
            (b'fLaC', '.flac'),            # FLAC
            (b'MThd', '.mid'),             # MIDI
        
        # 视频
            (b'\x00\x00\x00\x20\x66\x74\x79\x70', '.mp4'),  # MP4
            (b'RIFF', '.avi'),             # AVI
            (b'\x1A\x45\xDF\xA3', '.mkv'), # MKV
            (b'FLV\x01', '.flv'),         # FLV
            (b'\x00\x00\x01\xBA', '.mpg'), # MPEG
        
        # 压缩文件
            (b'\x50\x4B\x03\x04', '.zip'), # ZIP
            (b'\x52\x61\x72\x21', '.rar'), # RAR
            (b'\x1F\x8B\x08', '.gz'),      # GZIP
            (b'\x37\x7A\xBC\xAF', '.7z'),  # 7-Zip
        
        # 数据库
            (b'SQLite', '.sqlite'),        # SQLite
            (b'\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00', '.db3'), # SQLite3
        
        # 电子书
            (b'ITSF', '.chm'),             # CHM帮助文件
        
        # 其他
            (b'\x7B\x5C\x72\x74\x66\x31', '.rtf'), # RTF
            (b'\xEF\xBB\xBF', '.txt'),     # UTF-8 with BOM
            (b'\xFF\xFE', '.txt'),         # UTF-16 LE
            (b'\xFE\xFF', '.txt'),         # UTF-16 BE
        ]
        
        # 内置ZIP分析规则（优先级较低）
        self.internal_zip_rules = [
            ('.docx', 'word/document.xml'),
            ('.xlsx', 'xl/workbook.xml'),
            ('.pptx', 'ppt/presentation.xml'),
            ('.epub', 'mimetype'),
            ('.jar', 'META-INF/MANIFEST.MF'),
            ('.apk', 'AndroidManifest.xml'),
        ]
        
        # 外部规则（加载后优先级最高）
        self.external_signatures = []
        self.external_zip_rules = []
        
        if config_file and os.path.exists(config_file):
            self.load_external_config(config_file)
    
    def load_external_config(self, config_path):
        """加载外部配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                current_type = None
                
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('type='):
                        current_type = line.split('=', 1)[1].strip()
                    elif line.startswith('content='):
                        content = line.split('=', 1)[1].strip()
                        if content.startswith('\\x'):
                            # 处理十六进制格式
                            hex_str = content.replace('\\x', '')
                            try:
                                byte_content = bytes.fromhex(hex_str)
                                self.external_signatures.append((byte_content, current_type))
                            except ValueError:
                                print(f"配置错误: 无效的十六进制 '{content}'")
                        else:
                            # 处理普通文本
                            self.external_signatures.append((content.encode('ascii'), current_type))
                    elif line.startswith('zip='):
                        zip_rule = line.split('=', 1)[1].strip()
                        self.external_zip_rules.append((current_type, zip_rule))
                        
        except Exception as e:
            print(f"加载外部配置出错: {str(e)}")
    
    def recover_files(self, source_dir, target_dir):
        """执行文件恢复"""
        os.makedirs(target_dir, exist_ok=True)
        recovered_count = 0
        
        for filename in os.listdir(source_dir):
            if not filename.lower().endswith('.chk'):
                continue
                
            chk_path = os.path.join(source_dir, filename)
            try:
                # 合并所有规则（外部规则优先）
                all_signatures = self.external_signatures + self.internal_signatures
                all_zip_rules = self.external_zip_rules + self.internal_zip_rules
                
                # 识别文件类型
                with open(chk_path, 'rb') as f:
                    header = f.read(64)
                    extension = self.determine_file_type(header, all_signatures, all_zip_rules)
                
                # 生成唯一文件名
                base_name = os.path.splitext(filename)[0]
                new_filename = self.generate_unique_filename(target_dir, base_name, extension)
                
                # 恢复文件
                shutil.copy2(chk_path, os.path.join(target_dir, new_filename))
                recovered_count += 1
                print(f"已恢复: {filename} → {new_filename} ({extension})")
                
            except Exception as e:
                print(f"处理 {filename} 出错: {str(e)}")
        
        print(f"\n恢复完成! 共恢复了 {recovered_count} 个文件")
    
    def determine_file_type(self, header, signatures, zip_rules):
        """确定文件类型"""
        # 检查所有签名规则
        for sig, ext in signatures:
            if header.startswith(sig):
                if ext == '_ms_office_old':
                    return self.determine_office_type(header)
                elif ext == '_zip_analyze':
                    return self.analyze_zip_contents(header, zip_rules)
                return ext
        
        return '.bin'  # 默认未知类型
    
    def analyze_zip_contents(self, initial_header, zip_rules):
        """分析ZIP文件内容"""
        try:
            # 使用内存中的文件头创建一个临时文件对象
            fake_file = io.BytesIO(initial_header)
            
            # 尝试打开ZIP文件
            with zipfile.ZipFile(fake_file) as zip_ref:
                # 检查所有ZIP规则
                for ext, rule in zip_rules:
                    if rule.startswith('/'):
                        if rule[1:] in zip_ref.namelist():
                            return ext
                    elif rule == 'mimetype':
                        if 'mimetype' in zip_ref.namelist():
                            with zip_ref.open('mimetype') as f:
                                content = f.read(100).decode('ascii', 'ignore').strip()
                                if 'epub' in content.lower():
                                    return '.epub'
                                elif 'opendocument' in content.lower():
                                    if 'text' in content.lower():
                                        return '.odt'
                                    elif 'spreadsheet' in content.lower():
                                        return '.ods'
        except:
            pass
        
        return '.zip'  # 默认ZIP格式
    
    @staticmethod
    def determine_office_type(header):
        """识别Office旧格式"""
        office_markers = {
            b'WordDocument': '.doc',
            b'Workbook': '.xls',
            b'Book': '.xls',
            b'PowerPoint': '.ppt'
        }
        
        for marker, ext in office_markers.items():
            if marker in header:
                return ext
        
        return '.ole'  # 默认OLE格式
    
    @staticmethod
    def generate_unique_filename(directory, base_name, extension):
        """生成唯一的文件名"""
        counter = 0
        while True:
            new_name = f"{base_name}{extension}" if counter == 0 else f"{base_name}_{counter}{extension}"
            if not os.path.exists(os.path.join(directory, new_name)):
                return new_name
            counter += 1

def main():
    print("CHK文件恢复工具")
    print("=" * 60)
    print("特点:")
    print("- 内置常见文件格式识别")
    print("- 支持外部配置文件扩展")
    print("- 智能合并内外规则")
    print("=" * 60)
    
    config_file = input("外部配置文件路径（可选，直接回车跳过）: ").strip()
    source_dir = input("CHK文件所在目录: ").strip()
    target_dir = input("恢复文件输出目录: ").strip()
    
    if not os.path.isdir(source_dir):
        print("错误: 源目录不存在!")
        return
    
    # 初始化恢复引擎
    engine = FileRecoveryEngine(config_file if config_file and os.path.exists(config_file) else None)
    
    # 执行恢复
    engine.recover_files(source_dir, target_dir)

if __name__ == "__main__":
    main()
