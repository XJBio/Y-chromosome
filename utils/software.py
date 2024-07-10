import re
import logging
import subprocess
import os


def join_path(dir_path, name):
    return os.path.join(dir_path, name)


# 软件路径
USER_BASE = "/data/home/sjwan/"


# MINIMAP2 = "path/to/minimap2"
# RAGTAG = "path/to/ragtag"
# PBMM2 = 'path/to/pbmm2'
# NUCFLAG = 'path/to/nucflag'
# VERITYMAP = 'path/to/veritymap'
# UNIALIGNER = 'path/to/unialigner'
# SAMTOOLS = 'path/to/samtools'


# 通过这个文件，来选择固定版本的工具，进行调用


def setup_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def get_conda_envs():
    # 使用 subprocess.Popen 来激活环境并运行命令
    process = subprocess.Popen(
        ["/data/home/sjwan/miniconda3/bin/conda", "env", "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"Failed to list conda environments: {stderr}")
    return stdout


def parse_conda_envs(envs_output):
    interpreter_paths = {}
    lines = envs_output.strip().split("\n")
    for line in lines:
        if line.startswith("#") or line.strip() == "":
            continue
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0].rstrip("*")
            path = parts[-1]
            interpreter_path = os.path.join(path, "bin", "python")
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
    interpreter = INTERPRETER_PATH_CACHE.get(
        version, INTERPRETER_PATH_CACHE.get("base")
    )
    return interpreter


class ScriptExecutor:
    BASE_CMD = "{interpreter} {script} {pos_args} {opt_args}"

    def __init__(self, logger, version="default") -> None:
        self.INTERPRETER_PATH = get_interpreter_paths()
        self.interpreter = self.INTERPRETER_PATH.get(
            version, self.INTERPRETER_PATH.get("base")
        )
        self.logger = logger
        self.script = None
        self.pos_args = []
        self.opt_args = {}

    def set_script_and_args(self, script, pos_args=None, opt_args=None):
        """设置script、位置参数和选项参数"""
        self.script = script
        self.pos_args = pos_args if pos_args is not None else []
        self.opt_args = opt_args if opt_args is not None else {}

    def _format_args(self):
        """将位置参数和选项参数格式化为命令行字符串"""
        pos_args_str = " ".join(self.pos_args)
        opt_args_list = []
        for key, value in self.opt_args.items():
            if value is None:
                opt_args_list.append(f"{key}")
            else:
                opt_args_list.append(f"{key} {value}")
        opt_args_str = " ".join(opt_args_list)
        return pos_args_str, opt_args_str

    def run(self, mode="RUN"):
        # 确保 script 已设置
        if self.script is None:
            raise ValueError("Script must be set before running.")

        # 格式化参数
        pos_args_str, opt_args_str = self._format_args()

        # 构建命令字符串
        cmd = self.BASE_CMD.format(
            interpreter=self.interpreter,
            script=self.script,
            pos_args=pos_args_str,
            opt_args=opt_args_str,
        )

        # 执行命令或者仅打印命令
        if mode == "RUN":
            self.logger.info(f"Starting command: {cmd}")
            try:
                output = self._execute_command(cmd)
                self.logger.info(f"Ending command: {cmd}")
                return output
            except subprocess.CalledProcessError as e:
                raise e
        elif mode == "DEBUG":
            self.logger.debug(f"Command to be executed: {cmd}")
        else:
            raise ValueError("Invalid mode. Mode must be 'RUN' or 'DEBUG'.")

    def _execute_command(self, cmd):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            # Log the output with a preceding newline for better formatting
            self.logger.info(f"Output:\n{result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution failed: {e}")
            self.logger.error(f"Error Output:\n{e.stderr}")
            raise e


class BaseSoftware:
    EXE_PATH = {"default": "path/to/tools"}

    def __init__(self, logger, version="default") -> None:

        self.BASE_PARAMS = ["input", "output", "log", "exe_params"]

        self.BASE_CMD = "{exe_path} {exe_params} {input} {output} > {log}"

        self.RUN_PARAMS = {
            "input": "reference.fa",
            "output": "output_log",
            "exe_params": "soon",
        }
        self.exe = self.EXE_PATH.get(version, self.EXE_PATH["default"])
        self.logger = logger

    def run(self, mode="RUN"):
        # 构建命令字符串
        cmd = self.BASE_CMD.format(exe_path=self.exe, **self.RUN_PARAMS)
        # 执行命令或者仅打印命令
        if mode == "RUN":
            self.logger.info(f"Starting execute {self.__class__.__name__}: {cmd}")
            output = self._execute_command(cmd)
            self.logger.info(f"{self.__class__.__name__} executed: {cmd}")
            return output
        elif mode == "DEBUG":
            self.logger.debug(f"{self.__class__.__name__} to be executed: {cmd}")
        else:
            raise ValueError("Invalid mode. Mode must be 'RUN' or 'DEBUG'.")

    def _execute_command(self, cmd):
        # 实现命令执行的逻辑，这里只是示意
        # 如果命令执行失败，则抛出异常
        try:
            # 执行命令并捕获输出
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            self.logger.info(f"Command output:\n{result.stdout}")
            # self.logger.warning(f"Command error output:\n{result.stderr}")
            if result.stderr:
                self.logger.warning(f"Command error output:\n{result.stderr}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            # 记录错误并抛出异常

            self.logger.error(f"{self.__class__.__name__} execution failed: {cmd}")
            self.logger.error(f"Error output:\n{e.stderr}")
            raise e
        except Exception as e:
            # 记录其他异常并抛出
            self.logger.error(
                f"Unexpected error during {self.__class__.__name__} execution: {cmd}"
            )
            raise e


class Workflow:
    def __init__(self, logger):
        self.logger = logger
        self.tasks = []
        self.logger.info(INTERPRETER_PATH_CACHE)

    def add_script(self, script):
        self.tasks.append(script)

    def add_software(self, software):
        self.tasks.append(software)

    def run(self, mode="RUN"):
        self.logger.info("start workflow")
        for i, task in enumerate(self.tasks):

            if isinstance(task, ScriptExecutor):
                task.run(mode)
            elif isinstance(task, BaseSoftware):
                task.run(mode)
            else:
                self.logger.error("Unknown task type.")
                return
            self.logger.info(f"task finished {i+1}/{len(self.tasks)}")


class Remove(BaseSoftware):

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_PARAMS = ["files"]
        self.BASE_CMD = "rm -rf {files}"
        self.RUN_PARAMS = {"files": "{path}/{name}"}


class Minimap2_asm20(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/bio/bin/minimap2")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_PARAMS = ["target", "output", "query", "thread"]
        self.BASE_CMD = "{exe_path} -t {thread} -x asm20 -Y --secondary=yes -N 1 --cs -c --paf-no-hit {target} {query} > {output}"
        self.RUN_PARAMS = {
            "target": "{path}/{name}.fa",
            "query": "{path}/{name}.fa",
            "thread": "48",
            "output": "{path}/{name}.paf",
        }


class Minimap2_hifi(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/bio/bin/minimap2")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_PARAMS = ["target", "output", "query", "thread"]
        self.BASE_CMD = (
            "{exe_path} -t {thread} -ax map-hifi {target} {query} > {output}"
        )
        self.RUN_PARAMS = {
            "target": "{path}/{name}.fa",
            "query": "{path}/{name}.fa",
            "thread": "48",
            "output": "{path}/{name}.sam",
        }


class RagtagScaffoldDefaultMinimap(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/bio/bin/ragtag.py")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_PARAMS = ["reference", "query", "output", "thread"]
        self.BASE_CMD = (
            get_python_interpreter("bio")
            + " {exe_path} scaffold  -t {thread} {reference} {query} -o {output} "
        )
        self.RUN_PARAMS = {
            "reference": "{path}/{name}.fa",
            "query": "{path}/{name}.fa",
            "thread": "48",
            "output": "{path}/{name}",
        }


class Nucmer4(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "tools/mummer/bin/nucmer")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_PARAMS = ["reference", "query", "threads", "prefix"]
        self.BASE_CMD = "{exe_path} -p {prefix} -t {threads} {reference} {query}"
        self.RUN_PARAMS = {
            "reference": "{path}/{name}.fa",
            "query": "{path}/{name}.fa",
            "thread": "48",
            "prefix": "{path}/{name}",
        }


class Pbmm2_index(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/nucfreq/bin/pbmm2")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_PARAMS = ["contig", "mmi"]
        self.BASE_CMD = "{exe_path} index {contig} {mmi}"
        self.RUN_PARAMS = {"contig": "{path}/{name}.fa", "mmi": "{path}/{name}.mmi"}


class Pbmm2_align(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/nucfreq/bin/pbmm2")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_PARAMS = ["thread", "mmi", "fofn", "outbam"]
        self.BASE_CMD = "{exe_path} align --log-level DEBUG --preset SUBREAD --min-length 5000 -j {thread} {mmi} {fofn} {outbam} "
        self.RUN_PARAMS = {
            "thread": "48",
            "fofn": "{path}/{name}.fofn",
            "mmi": "{path}/{name}.mmi",
            "outbam": "{path}/{name}.bam",
        }


class Samtools_view_sam2bam(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/bio/bin/samtools")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = "{exe_path} view -@ {thread} -Sb {inputsam} > {outbam}"
        self.BASE_PARAMS = ["thread", "outbam", "inputsam"]
        self.RUN_PARAMS = {
            "thread": "4",
            "outbam": "{path}/{name}.bam",
            "inputsam": "{path}/{name}.sam",
        }


class Samtools_view_2308(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/bio/bin/samtools")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = "{exe_path} view -@ {thread} -F 2308 -u -o {outbam} {inputbam}"
        self.BASE_PARAMS = ["thread", "outbam", "inputbam"]
        self.RUN_PARAMS = {
            "thread": "4",
            "outbam": "{path}/{name}.bam",
            "inputbam": "{path}/{name}.bam",
        }


class Samtools_view_name(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/bio/bin/samtools")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = "{exe_path} view -@ {thread}  -b {inputbam} {name} > {outbam}"
        self.BASE_PARAMS = ["name", "outbam", "thread", "inputbam"]
        self.RUN_PARAMS = {
            "thread": "4",
            "name": "name",
            "outbam": "{path}/{name}.bam",
            "inputbam": "{path}/{name}.bam",
        }


class Samtools_depth(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/bio/bin/samtools")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = "{exe_path} depth -a {inputbam} > {depth}"
        self.BASE_PARAMS = ["depth", "inputbam"]
        self.RUN_PARAMS = {
            "inputbam": "{path}/{name}.bam",
            "depth": "{path}/{name}.depth",
        }


class Samtools_sort_bam(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/verkko2/bin/samtools")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = "{exe_path} sort -@ {thread} -o {outbam} {inputbam}"
        self.BASE_PARAMS = ["thread", "outbam", "inputbam"]
        self.RUN_PARAMS = {
            "thread": "4",
            "outbam": "{path}/{name}.bam",
            "inputbam": "{path}/{name}.bam",
        }


class Samtools_index_bam(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/verkko2/bin/samtools")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = "{exe_path} index -@ {thread} {inputbam}"
        self.BASE_PARAMS = ["thread", "inputbam"]
        self.RUN_PARAMS = {
            "thread": "4",
            "inputbam": "{path}/{name}.bam",
        }
        
class Samtools_bam2fq(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "miniconda3/envs/verkko2/bin/samtools")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = "{exe_path} fastq  -@ {thread}  {inputbam} > {outputfq} "
        self.BASE_PARAMS = ["thread", "inputbam",'outputfq']
        self.RUN_PARAMS = {
            "thread": "4",
            "inputbam": "{path}/{name}.bam",
            "outputfq": "{path}/{name}.fq",
        }


class VerityMap(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "tools/VerityMap/veritymap/main.py")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)

        self.BASE_CMD = (
            get_python_interpreter("bio")
            + " {exe_path} -t {thread}  -o {output} -d {hifi} --reads {reads} {assembly}"
        )
        self.BASE_PARAMS = ["thread", "output", "hifi", "reads", "assembly"]
        self.RUN_PARAMS = {
            "thread": "4",
            "output": "{path}/{name}",
            "hifi": "hifi-diploid",
            "reads": "{path}/{name}",
            "assembly": "{path}/{name}.fa",
        }


class Nucflag(BaseSoftware):
    EXE_PATH = {"default": join_path(USER_BASE, "tools/NucFlag/venv/bin/nucflag")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)
        self.BASE_CMD = "{exe_path} -i {contigbam} -b {region} -c {toml} -d {imgout} -o {misasm} -s {status} -t {thread} -p {thread}"
        self.BASE_PARAMS = [
            "thread",
            "contigbam",
            "region",
            "toml",
            "imgout",
            "misasm",
            "status",
        ]
        self.RUN_PARAMS = {
            "thread": "4",
            "contigbam": "{path}/{name}.bam",
            "region": "{path}/{name}.bed",
            "toml": "{path}/{name}.toml",
            "imgout": "{path}/{name}",
            "misasm": "{path}/{name}.bed",
            "status": "{path}/{name}.bed",
        }


class UniAligner(BaseSoftware):

    EXE_PATH = {
        "default": join_path(
            USER_BASE, "tools/unialigner/tandem_aligner/build/bin/tandem_aligner"
        )
    }

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)
        self.BASE_CMD = "{exe_path} --first {first} --second {second}  -o {output_dir}"
        self.BASE_PARAMS = ["first", "second", "output_dir"]
        self.RUN_PARAMS = {
            "first": "{path}/{name}.fa",
            "second": "{path}/{name}.fa",
            "output_dir": "{path}/{name}",
        }


class Rukki(BaseSoftware):

    EXE_PATH = {"default": join_path(USER_BASE, "tools/rukki/target/release/rukki")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)
        self.BASE_CMD = "{exe_path} trio -g {assembly_graph} -m {XY_contig_table} -p {out_paths} --final-assign {out_node_assignment} --try-fill-bubbles --min-gap-size 1 --default-gap-size 1000"
        self.BASE_PARAMS = [
            "assembly_graph",
            "XY_contig_table",
            "out_paths",
            "out_node_assignment",
        ]
        self.RUN_PARAMS = {
            "assembly_graph": "{path}/{name}.gfa",
            "XY_contig_table": "{path}/{name}.tsv",
            "out_paths": "{path}/{name}.tsv",
            "out_node_assignment": "{path}/{name}.tsv",
        }


# class DeepVariant_make_example(BaseSoftware):

#     EXE_PATH = {
#         'default': join_path(USER_BASE, 'miniconda3/envs/deepvariant/bin/dv_make_examples.py')
#     }

#     def __init__(self, logger, version='default') :
#         super().__init__(logger, version)
#         self.BASE_CMD = get_python_interpreter('deepvariant') + '{exe_path} '
#         self.BASE_PARAMS = ['assembly_graph', 'XY_contig_table', 'out_paths','out_node_assignment']
#         self.RUN_PARAMS = {
#             'assembly_graph':'{path}/{name}.gfa',
#             'XY_contig_table':'{path}/{name}.tsv',
#             'out_paths':'{path}/{name}.tsv',
#             'out_node_assignment':'{path}/{name}.tsv'
#         }


class HMMER_nhmmer(BaseSoftware):

    EXE_PATH = {"default": join_path(USER_BASE, "tools/hmmer-3.4/bin/nhmmer")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)
        self.BASE_CMD = "{exe_path} --cpu {threads} --dna -o {output_txt} --tblout {output_table} -E 1.60E-150 {query_motif} {assembly}"
        self.BASE_PARAMS = [
            "threads",
            "output_txt",
            "output_table",
            "query_motif",
            "assembly",
        ]
        self.RUN_PARAMS = {
            "threads": "48",
            "output_txt": "{path}/{name}.txt",
            "output_table": "{path}/{name}.tab",
            "query_motif": "{path}/{name}.fa",
            "assembly": "{path}/{name}.fa",
        }


class StringDecomposer(BaseSoftware):

    EXE_PATH = {
        "default": join_path(USER_BASE, "miniconda3/envs/bio/bin/stringdecomposer")
    }

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)
        logger.info(f"{self.EXE_PATH['default']}")
        self.BASE_CMD = "{exe_path} -t {threads}  -o {out_dir}  {sequences} {monomers}"
        self.BASE_PARAMS = ["threads", "out_dir", "sequences", "monomers"]
        self.RUN_PARAMS = {
            "threads": "48",
            "out_dir": "{path}/{name}",
            "sequences": "{path}/{name}.fa",
            "monomers": "{path}/{name}.fa",
        }


class RepeatMasker(BaseSoftware):

    EXE_PATH = {"default": join_path(USER_BASE, "tools/RepeatMasker/RepeatMasker")}

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)
        logger.info(f"{self.EXE_PATH['default']}")
        self.BASE_CMD = "{exe_path} -species human -e hmmer -dir {out_dir} -pa {threads} {sequences}"
        self.BASE_PARAMS = ["threads", "out_dir", "sequences"]
        self.RUN_PARAMS = {
            "threads": "48",
            "out_dir": "{path}/{name}",
            "sequences": "{path}/{name}.fa",
        }


class HumAS_HMMER(BaseSoftware):

    EXE_PATH = {
        "default": join_path(USER_BASE, "tools/HumAS-HMMER_for_AnVIL/hmmer-run.sh")
    }

    def __init__(self, logger, version="default"):
        super().__init__(logger, version)
        logger.info(f"{self.EXE_PATH['default']}")
        self.BASE_CMD = (
            "sh {exe_path} {fa_dir}"
            + " /data/home/sjwan/tools/HumAS-HMMER_for_AnVIL/AS-HORs-hmmer3.3.2-120124.hmm" 
            + " {threads}"
        )
        self.BASE_PARAMS = ["threads", "fa_dir", "sequences"]
        self.RUN_PARAMS = {
            "threads": "48",
            "fa_dir": "{path}/{name}",
        }
