import subprocess
import os
import logging

# 缓存解释器路径
INTERPRETER_PATH_CACHE = None

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

def get_interpreter_paths():
    global INTERPRETER_PATH_CACHE
    if INTERPRETER_PATH_CACHE is None:
        envs_output = get_conda_envs()
        INTERPRETER_PATH_CACHE = parse_conda_envs(envs_output)
    return INTERPRETER_PATH_CACHE

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

# 示例用法
logger = setup_logger('script_executor.log')
executor = ScriptExecutor(logger, version='bio')
script = 'example.py'
args = '--option value'
log_file = 'script_output.log'
executor.run(script, args, mode='RUN')
executor.run(script, args, mode='DEBUG')
