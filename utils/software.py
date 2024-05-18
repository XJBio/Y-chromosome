import re
import logging
import subprocess
import os

# 软件路径
USE_BASE="/data/home/sjwan/"
MINIMAP2 = "path/to/minimap2"
RAGTAG = "path/to/ragtag"
PBMM2 = 'path/to/pbmm2'
NUCFLAG = 'path/to/nucflag'
VERITYMAP= 'path/to/veritymap'
UNIALIGNER= 'path/to/unialigner'
SAMTOOLS = 'path/to/samtools'

# 通过这个文件，来选择固定版本的工具，进行调用


def setup_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger



def get_conda_envs():
    result = subprocess.run(['conda', 'env', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to list conda environments: {result.stderr}")
    return result.stdout

def parse_conda_envs(envs_output):
    interpreter_paths = {}
    lines = envs_output.strip().split('\n')
    for line in lines:
        if line.startswith('#') or line.strip() == "":
            continue
        parts = line.split()
        if len(parts) == 1:
            # 忽略不完整路径
            continue
        elif len(parts) == 2:
            name, path = parts
            interpreter_path = os.path.join(path, 'bin', 'python')
            interpreter_paths[name] = interpreter_path
    return interpreter_paths

# 缓存解释器路径
INTERPRETER_PATH_CACHE = parse_conda_envs(get_conda_envs())

def get_interpreter_paths():
    global INTERPRETER_PATH_CACHE
    if INTERPRETER_PATH_CACHE is None:
        envs_output = get_conda_envs()
        INTERPRETER_PATH_CACHE = parse_conda_envs(envs_output)
    return INTERPRETER_PATH_CACHE

def get_python_interpreter(version):
    global INTERPRETER_PATH_CACHE
    return INTERPRETER_PATH_CACHE.get(version, INTERPRETER_PATH_CACHE.get('base'))

class ScriptExecutor:
    
    def __init__(self, logger, version='default') -> None:
        self.INTERPRETER_PATH = get_interpreter_paths()
        self.interpreter = self.INTERPRETER_PATH.get(version, self.INTERPRETER_PATH.get('base'))
        self.logger = logger
    
    BASE_CMD = '{interpreter} {script} {args}'
    

    def run(self, script, args, mode='RUN'):
        # 构建命令字符串
        cmd = self.BASE_CMD.format(interpreter=self.interpreter, script=script, args=args)
        
        # 执行命令或者仅打印命令
        if mode == 'RUN':
            self.logger.info(f"Starting command: {cmd}")
            try:
                output = self._execute_command(cmd)
                self.logger.info(f"Ending command: {cmd}")
                return output
            except subprocess.CalledProcessError as e:
                raise e
        elif mode == 'DEBUG':
            self.logger.debug(f"Command to be executed: {cmd}")
        else:
            raise ValueError("Invalid mode. Mode must be 'RUN' or 'DEBUG'.")
    
    def _execute_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # Log the output with a preceding newline for better formatting
            self.logger.info(f"Output:\n{result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution failed: {e}")
            self.logger.error(f"Error Output:\n{e.stderr}")
            raise e

class BaseSoftware:
    
    EXE_PATH = {
        'default': 'path/to/tools'
    }
    
    BASE_PARAMS = ['input', 'output', 'log', 'exe_params']
    
    BASE_CMD = '{exe_path} {exe_params} {input} {output} > {log}'
    
    RUN_PARAMS = {'input': 'reference.fa', 'output': 'output_log', 'exe_params': 'soon'}
    
    def __init__(self, logger, version='default') -> None:
        self.exe = self.EXE_PATH.get(version, self.EXE_PATH['default'])
        self.logger = logger
    
    def run(self, mode='RUN'):
        # 构建命令字符串
        cmd = self.BASE_CMD.format(exe_path=self.exe, **self.RUN_PARAMS)
        
        # 执行命令或者仅打印命令
        if mode == 'RUN':
            self.logger.info(f"Starting excute {self.__class__.__name__}: {cmd}")
            output = self._execute_command(cmd)
            self.logger.info(f"{self.__class__.__name__} executed: {cmd}")
            return output
        elif mode == 'DEBUG':
            self.logger.debug(f"{self.__class__.__name__} to be executed: {cmd}")
        else:
            raise ValueError("Invalid mode. Mode must be 'RUN' or 'DEBUG'.")
    
    def _execute_command(self, cmd):
        # 实现命令执行的逻辑，这里只是示意
        # 如果命令执行失败，则抛出异常
        try:
            # 执行命令
            subprocess.run(cmd, shell=True, check=True)
            return "Command output"
        except Exception as e:
            # 记录错误并抛出异常
            self.logger.error(f"{self.__class__.__name__} execution failed: {cmd}")
            raise e

class Workflow:
    def __init__(self, logger):
        self.logger = logger
        self.tasks = []

    def add_script(self,  script, args):
        self.tasks.append((ScriptExecutor(self.logger), script, args))

    def add_software(self, software):
        self.tasks.append((software, 0))

    def run(self, mode='RUN'):
        for task in self.tasks:
            if isinstance(task[0], ScriptExecutor):
                script_executor, script, args = task
                script_executor.run(script, args, mode)
            elif isinstance(task[0], BaseSoftware):
                software, _ = task
                software.run(mode)
            else:
                self.logger.error("Unknown task type.")
                

class Minimap2(BaseSoftware):
    
    EXE_PATH = {
        'default': '/usr/bin/minimap2'
    }
    
    BASE_PARAMS = ['input', 'output', 'log', 'threads']
    
    BASE_CMD = '{exe_path} -t {threads} {input} > {output} 2> {log}'
    

class RagtagScaffold(BaseSoftware):
    EXE_PATH = {
        'default': USE_BASE + '/miniconda3/envs/bio/bin/ragtag.py'
    }
    BASE_PARAMS = ['reference', 'query', 'output', 'threads']
    BASE_CMD = get_python_interpreter('bio') + ' {exe_path} scaffold  -t {threads} {reference} {query} -o {output} '

class Nucmer4(BaseSoftware):
    EXE_PATH = {
        'default': USE_BASE + '/tools/mummer/bin/nucmer'
    }
    BASE_PARAMS = ['reference','query','threads', 'prefix']
    BASE_CMD = '{exe_path} -p {prefix} -t {threads} {reference} {query}'


class VerityMap(BaseSoftware):
    EXE_PATH = {
        'default': USE_BASE + '/tools/VerityMap/veritymap/main.py'
    }
    BASE_PARAMS = ['threads', 'reads_file', 'hifiont', 'output_dir', 'assembly_file1', 'assembly_file2']
    BASE_CMD = get_python_interpreter('bio') + ' {exe_path} veritymap/main.py -t {threads}  --reads {reads_file} -d {hifiont} -o {output_dir} {assembly_file1} {assembly_file2}'


class Pbmm2_index(BaseSoftware):
    EXE_PATH = {
        'default': USE_BASE + '/miniconda3/envs/nucfreq/bin/pbmm2'
    }
    BASE_PARAMS = ['contig', 'mmi']
    BASE_CMD = '{exe_path} index {contig} {mni}'
    RUN_PARAMS = {'contig': '{path}/{name}.fa', 'mni':'{path}/{name}.mni'}

class Pbmm2_align(BaseSoftware):
    EXE_PATH = {
        'default': USE_BASE + '/miniconda3/envs/nucfreq/bin/pbmm2'
    }
    BASE_PARAMS = ['thread', 'mmi', 'fofn','outbam']
    BASE_CMD = '{exe_path} align --log-level DEBUG --preset SUBREAD --min-length 5000 -j {thread} {mmi} {fofn} {outbam} '
    RUN_PARAMS = {'thread':'48', 
                  'fofn': '{path}/{name}.fofn', 
                  'mni':'{path}/{name}.mni', 
                  'outbam':'{path}/{name}.bam'
                  }


