import re
import copy
import math
import os
import shutil
import textwrap
import threading
import time
from pathlib import Path
from pydub import AudioSegment
from typing import Dict

from videotrans import translator
from videotrans.recognition import run as run_recogn
from videotrans.translator import run as run_trans,get_audio_code
from videotrans.tts import run as run_tts
from videotrans.configure import config
from videotrans.configure._except import LogExcept
from videotrans.util import tools

from ._rate import SpeedRate
from ._base import BaseTask

class TransCreate(BaseTask):
    """
    obj={name,dirname,basename,noextname,ext,target_dir,uuid}
    """
    def __init__(self, config_params: Dict = None, obj:Dict=None):
        super().__init__(config_params,obj)

        # 存在添加的背景音乐
        if tools.vail_file(self.config_params['back_audio']):
            self.init['background_music'] = Path(self.config_params['back_audio']).as_posix()

        # 如果不是仅提取，则获取视频信息
        if self.config_params['app_mode'] not in ['tiqu']:
            # 获取视频信息
            try:
                self._signal(text="分析视频数据，用时可能较久请稍等.." if config.defaulelang == 'zh' else "Hold on a monment")
                self.init['video_info'] = tools.get_video_info(self.init['name'])
            except Exception as e:
                raise LogExcept(f"{config.transobj['get video_info error']}:{str(e)}")

            if not self.init['video_info']:
                raise LogExcept(config.transobj['get video_info error'])
            video_codec = 'h264' if self.video_codec == 264 else 'hevc'
            if self.init['video_info']['video_codec_name'] == video_codec and self.init['ext'].lower() == 'mp4':self.init['h264'] = True

        # 临时文件夹
        self.init['cache_folder'] = f"{config.TEMP_DIR}/{self.init['noextname']}"
        self.init['target_dir'] = Path(self.init['target_dir']).as_posix()
        # 创建文件夹
        Path(self.init['target_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.init['cache_folder']).mkdir(parents=True, exist_ok=True)

        # 原始语言代码
        source_code = self.config_params['source_language'] if self.config_params['source_language'] in config.langlist else config.rev_langlist.get(
            self.config_params['source_language'], None)
        if source_code:
            self.init['source_language_code'] = source_code
        # 目标语言代码
        target_code = self.config_params['target_language'] if self.config_params['target_language'] in config.langlist else config.rev_langlist.get(
            self.config_params['target_language'], None)
        if target_code:
            self.init['target_language_code'] = target_code

        # 检测字幕原始语言
        self.init['detect_language'] = get_audio_code(show_source=self.init['source_language_code'])

        # 存放分离后的无声音mp4
        self.init['novoice_mp4'] = f"{self.init['target_dir']}/novoice.mp4"
        # 原始语言一定存在
        self.init['source_sub'] = f"{self.init['target_dir']}/{self.init['source_language_code']}.srt"
        self._unlink_size0(self.init['source_sub'])

        # 原始语言wav
        self.init['source_wav'] = f"{self.init['target_dir']}/{self.init['source_language_code']}.m4a"
        self._unlink_size0(self.init['source_wav'])

        # 目标语言字幕文件
        if self.init['target_language_code']:
            self.init['target_sub'] = f"{self.init['target_dir']}/{self.init['target_language_code']}.srt"
            self._unlink_size0(self.init['target_sub'])
            # 配音后的目标语言音频文件
            self.init['target_wav'] = f"{self.init['target_dir']}/{self.init['target_language_code']}.m4a"
            self._unlink_size0(self.init['target_wav'])

        # 是否需要语音识别:只要不存在原始语言字幕文件就需要识别
        if not Path(self.init['source_sub']).exists():
            self.shoud_recogn = True
            # 作为识别音频
            self.init['shibie_audio'] = f"{self.init['target_dir']}/shibie.wav"
            self._unlink_size0(self.init['shibie_audio'])

        # 是否需要翻译:存在目标语言代码并且不等于原始语言，并且不存在目标字幕文件，则需要翻译
        if self.init['target_language_code'] and self.init['target_language_code'] != self.init[
            'source_language_code'] and not Path(self.init['target_sub']).exists():
            self.shoud_trans = True

        # 如果原语言和目标语言相等，并且存在配音角色，则替换配音
        if self.config_params['voice_role'] != 'No' and self.init['source_language_code'] == self.init[
            'target_language_code']:
            self.init['target_wav'] = f"{self.init['target_dir']}/{self.init['target_language_code']}-dubbing.m4a"
            self._unlink_size0(self.init['target_wav'])
        # 如果配音角色不是No 并且不存在目标音频，则需要配音
        if self.config_params['voice_role'] != 'No':
            self.shoud_dubbing = True

        # 如果不是tiqu，则均需要合并
        if self.config_params['app_mode'] != 'tiqu':
            self.shoud_hebing = True

        # 最终需要输出的mp4视频
        self.init['targetdir_mp4'] = f"{self.init['target_dir']}/{self.init['noextname']}.mp4"
        self._unlink_size0(self.init['targetdir_mp4'])
        # 是否需要背景音分离：分离出的原始音频文件
        if self.config_params['is_separate']:
            # 背景音乐
            self.init['instrument'] = f"{self.init['target_dir']}/instrument.wav"
            # 转为8k采样率，降低文件
            self.init['vocal'] = f"{self.init['target_dir']}/vocal.wav"
            self.shoud_separate = True
            self._unlink_size0(self.init['instrument'])
            self._unlink_size0(self.init['vocal'])

        # 如果存在字幕，则视为原始语言字幕，不再识别
        if "subtitles" in self.config_params and self.config_params['subtitles'].strip():
            # 如果不存在目标语言，则视为原始语言字幕
            sub_file = self.init['source_sub']
            with open(sub_file, 'w', encoding="utf-8", errors="ignore") as f:
                txt = re.sub(r':\d+\.\d+', lambda m: m.group().replace('.', ','),
                             self.config_params['subtitles'].strip(), re.S | re.M)
                f.write(txt)
            self.shoud_recogn = False
        config.logger.info(f"{self.init=}")
        # 获取set.ini配置
        config.settings = config.parse_init()
        # 禁止修改字幕
        self._signal(text="forbid" if self.config_params['is_batch'] else "no", type="disabled_edit")

        # 开启一个线程读秒
        def runing():
            if self._exit():
                return
            t = 0
            while not self.hasend:
                time.sleep(2)
                t += 2
                self._signal(text=f"{self.status_text} {t}s???{self.precent}", type="set_precent", nologs=True)
        threading.Thread(target=runing).start()


    # 启动执行入口
    def prepare(self):
        if self._exit():
            return
        # 将原始视频分离为无声视频和音频
        self._split_wav_novicemp4()
        return True

    def _recogn_succeed(self):
        # 仅提取字幕
        self.precent+=5
        if self.config_params['app_mode'] == 'tiqu':
            shutil.copy2(self.init['source_sub'], f"{self.init['target_dir']}/{self.init['noextname']}.srt")
            if not self.shoud_trans:
                self.hasend = True
                self.precent = 100
        self.status_text = config.transobj['endtiquzimu']
    # 开始识别
    def recogn(self):
        if self._exit():
            return
        if not self.shoud_recogn:
            return True
        self.status_text = config.transobj['kaishitiquzimu']
        self.precent += 3
        self._signal(text=config.transobj["kaishishibie"])
        if tools.vail_file(self.init['source_sub']):
            self._recogn_succeed()
            return True
        # 分离未完成，需等待
        while not tools.vail_file(self.init['source_wav']):
            self._signal(text=config.transobj["running"])
            time.sleep(1)

        try:
            if not tools.vail_file(self.init['shibie_audio']):
                tools.conver_to_16k(self.init['source_wav'], self.init['shibie_audio'])
            #todo
            self.status_text = '语音识别文字处理中' if config.defaulelang == 'zh' else 'Speech Recognition to Word Processing'
            raw_subtitles = run_recogn(
                # faster-whisper openai-whisper googlespeech
                model_type=self.config_params['model_type'],
                # 整体 预先 均等
                type=self.config_params['whisper_type'],
                uuid=self.uuid,
                # 模型名
                model_name=self.config_params['whisper_model'],
                # 识别音频
                audio_file=self.init['shibie_audio'],
                detect_language=self.init['detect_language'],
                cache_folder=self.init['cache_folder'],
                is_cuda=self.config_params['cuda'],
                inst=self)
            Path(self.init['shibie_audio']).unlink(missing_ok=True)
        except Exception as e:
            msg = f'{str(e)}{str(e.args)}'
            if re.search(r'cub[a-zA-Z0-9_.-]+?\.dll', msg, re.I | re.M) is not None:
                msg = f'【缺少cuBLAS.dll】请点击菜单栏-帮助/支持-下载cublasxx.dll,或者切换为openai模型 {msg} ' if config.defaulelang == 'zh' else f'[missing cublasxx.dll] Open menubar Help&Support->Download cuBLASxx.dll or use openai model {msg}'
            elif re.search(r'out\s+?of.*?memory', msg, re.I):
                msg = f'显存不足，请使用较小模型，比如 tiny/base/small {msg}' if config.defaulelang == 'zh' else f'Insufficient video memory, use a smaller model such as tiny/base/small {msg}'
            elif re.search(r'cudnn', msg, re.I):
                msg = f'cuDNN错误，请尝试升级显卡驱动，重新安装CUDA12.x和cuDNN9 {msg}' if config.defaulelang == 'zh' else f'cuDNN error, please try upgrading the graphics card driver and reinstalling CUDA12.x and cuDNN9 {msg}'
            self.hasend = True
            tools.send_notification(str(e), f'{self.init["basename"]}')
            raise LogExcept(f'{msg}')
        else:
            if self._exit():
                return
            if not raw_subtitles or len(raw_subtitles) < 1:
                raise LogExcept(
                    self.init['basename'] + config.transobj['recogn result is empty'].replace('{lang}',self.config_params['source_language']))
            self._save_srt_target(raw_subtitles, self.init['source_sub'])
            self._recogn_succeed()
        return True

    def trans(self):
        if self._exit():
            return
        if not self.shoud_trans:
            return True
        self.status_text = config.transobj['starttrans']
        config.task_countdown = 0 if self.config_params['app_mode'] == 'biaozhun_jd' else int(
            config.settings['countdown_sec'])
        # 如果存在目标语言字幕，前台直接使用该字幕替换
        if self._srt_vail(self.init['target_sub']):
            # 判断已存在的字幕文件中是否存在有效字幕纪录
            # 通知前端替换字幕
            with open(self.init['target_sub'], 'r', encoding="utf-8", errors="ignore") as f:
                self._signal(text=f.read().strip(), type='replace_subtitle')
                return True
        # 单个允许修改字幕
        if not self.config_params['is_batch']:
            # 设置secwin中wait_subtitle为原始语言字幕文件
            self._signal(text=self.init['source_sub'], type='set_source_sub')
            # 等待编辑原字幕后翻译,允许修改字幕
            self._signal(text=config.transobj["xiugaiyuanyuyan"], type='edit_subtitle_source')
            while config.task_countdown > 0:
                config.task_countdown -= 1
                if config.task_countdown <= config.settings['countdown_sec']:
                    self._signal(text=f"{config.task_countdown} {config.transobj['jimiaohoufanyi']}", type='show_djs')
                time.sleep(1)
            # 禁止修改字幕
            self._signal(text='translate_start', type='timeout_djs')
            time.sleep(2)

        self._signal(text=config.transobj['starttrans'])
        # 开始翻译,从目标文件夹读取原始字幕
        rawsrt = tools.get_subtitle_from_srt(self.init['source_sub'], is_file=True)
        if not rawsrt or len(rawsrt) < 1:
            raise LogExcept(f'{self.init["basename"]}' + config.transobj['No subtitles file'])

        try:
            #todo
            self.status_text = config.transobj['kaishitiquhefanyi']
            target_srt = run_trans(
                translate_type=self.config_params['translate_type'],
                text_list=rawsrt,
                target_language_name=self.config_params['target_language'],
                inst=self,
                uuid=self.uuid,
                source_code=self.init['source_language_code'])
        except Exception as e:
            self.hasend = True
            tools.send_notification(str(e), f'{self.init["basename"]}')
            raise LogExcept(e)
        else:
            self._save_srt_target(target_srt, self.init['target_sub'])
            # 仅提取，该名字删原
            if self.config_params['app_mode'] == 'tiqu':
                shutil.copy2(self.init['target_sub'],f"{self.init['target_dir']}/{self.init['noextname']}-{self.init['target_language_code']}.srt")
                self.hasend = True
                self.precent = 100
        self.status_text = config.transobj['endtrans']
        return True

    def dubbing(self):
        if self._exit():
            return
        if self.config_params['app_mode'] == 'tiqu':
            self.precent = 100
            return True
        if not self.shoud_dubbing:
            return True
        self.status_text = config.transobj['kaishipeiyin']
        self.precent += 3
        config.task_countdown = 0 if self.config_params['app_mode'] == 'biaozhun_jd' else int(
            config.settings['countdown_sec'])

        # 允许修改字幕
        if not self.config_params['is_batch']:
            self._signal(text=self.init['target_sub'], type='set_target_sub')
            self._signal(text=config.transobj["xiugaipeiyinzimu"], type="edit_subtitle_target")
            while config.task_countdown > 0:
                # 其他情况，字幕处理完毕，未超时，等待1s，继续倒计时
                time.sleep(1)
                # 倒计时中
                config.task_countdown -= 1
                if config.task_countdown <= int(config.settings['countdown_sec']):
                    self._signal(text=f"{config.task_countdown}{config.transobj['zidonghebingmiaohou']}",
                                      type='show_djs')
            # 禁止修改字幕
            self._signal(text='dubbing_start', type='timeout_djs')
        self._signal(text=config.transobj['kaishipeiyin'])
        time.sleep(3)

        try:
            #todo
            self._before_tts()
            self._exec_tts()
        except Exception as e:
            self.hasend = True
            tools.send_notification(str(e), f'{self.init["basename"]}')
            raise LogExcept(e)
        if self.config_params['app_mode'] in ['tiqu']:
            self.precent = 100
        return True

    def align(self):
        if self._exit():
            return
        if self.config_params['app_mode'] == 'tiqu':
            self.precent = 100
            return True

        if not self.shoud_dubbing:
            return True
        self.status_text = config.transobj['duiqicaozuo']
        self.precent += 3
        if self.config_params['voice_autorate'] or self.config_params['video_autorate']:
            self.status_text = '声画变速对齐阶段' if config.defaulelang == 'zh' else 'Sound & video speed alignment stage'
        try:
            #todo
            rate_inst = SpeedRate(
                queue_tts=self.queue_tts,
                uuid=self.uuid,
                shoud_audiorate=self.config_params['voice_autorate'] and int(config.settings['audio_rate']) > 1,
                shoud_videorate=self.config_params['video_autorate'] and int(config.settings['video_rate']) > 1,
                novoice_mp4=self.init['novoice_mp4'],
                noextname=self.init['noextname'],
                target_audio=self.init['target_wav']
            )
            self.queue_tts = rate_inst.run()
            # 更新字幕
            srt = ""
            for (idx, it) in enumerate(self.queue_tts):
                if not config.settings['force_edit_srt']:
                    it['startraw'] = tools.ms_to_time_string(ms=it['start_time_source'])
                    it['endraw'] = tools.ms_to_time_string(ms=it['end_time_source'])
                srt += f"{idx + 1}\n{it['startraw']} --> {it['endraw']}\n{it['text']}\n\n"
            # 字幕保存到目标文件夹
            Path(self.init['target_sub']).write_text(srt.strip(), encoding="utf-8", errors="ignore")
        except Exception as e:
            self.hasend = True
            tools.send_notification(str(e), f'{self.init["basename"]}')
            raise LogExcept(e)
        return True

    def hebing(self):
        if self._exit():
            return
        if not self.shoud_hebing:
            self.precent = 100
            return True
        if self.precent < 95:
            self.precent += 3
        self.status_text = config.transobj['kaishihebing']
        try:
            #todo
            self._compos_video()
        except Exception as e:
            self.hasend = True
            tools.send_notification(str(e), f'{self.init["basename"]}')
            raise LogExcept(e)
        self.precent = 100
        return True

    # 收尾，根据 output和 linshi_output是否相同，不相同，则移动
    def move_at_end(self):
        # 正常完成仍是 ing，手动停止变为 stop
        if self._exit():
            return
        self.hasend = True
        self.precent = 100

        # 提取时，删除
        if self.config_params['app_mode'] == 'tiqu':
            Path(f"{self.init['target_dir']}/{self.init['source_language_code']}.srt").unlink(missing_ok=True)
            Path(f"{self.init['target_dir']}/{self.init['target_language_code']}.srt").unlink(missing_ok=True)
        # 仅保存视频
        elif self.config_params['only_video']:
            outputpath = Path(self.init['target_dir'])
            for it in outputpath.iterdir():
                ext = it.suffix.lower()
                if ext != '.mp4':
                    it.unlink(missing_ok=True)
                else:
                    try:
                        shutil.copy2(Path(it).as_posix(),(it.parent / "../" / f'{it.name}').resolve().as_posix())
                    except Exception:
                        pass
            try:
                self.init['target_dir'] = outputpath.parent.resolve().as_posix()
                shutil.rmtree(outputpath.as_posix(), ignore_errors=True)
            except Exception:
                pass

        self._signal(text=f"{self.init['name']}",type='succeed')
        tools.send_notification("Succeed", f"{self.init['basename']}")
        return True

    # 分离音频 和 novoice.mp4
    def _split_wav_novicemp4(self):
        # 不是 提取字幕时，需要分离出视频
        if self.config_params['app_mode'] not in ['tiqu']:
            config.queue_novice[self.init['noextname']] = 'ing'
            threading.Thread(
                target=tools.split_novoice_byraw,
                args=(self.init['name'],
                      self.init['novoice_mp4'],
                      self.init['noextname'],
                      "copy" if self.init['h264'] else f"libx{self.video_codec}")).start()
            if not self.init['h264']:
                self.status_text = '视频需要转码，耗时可能较久..' if config.defaulelang == 'zh' else 'Video needs transcoded and take a long time..'
        else:
            config.queue_novice[self.init['noextname']] = 'end'

        # 添加是否保留背景选项
        if self.config_params['is_separate']:
            try:
                self._signal(text=config.transobj['Separating background music'])
                self.status_text = config.transobj['Separating background music']
                tools.split_audio_byraw(
                    self.init['name'],
                    self.init['source_wav'],
                    True,
                    uuid=self.uuid)
            except Exception as e:
                pass
            finally:
                if not tools.vail_file(self.init['vocal']):
                    # 分离失败
                    self.init['instrument'] = None
                    self.init['vocal'] = None
                    self.config_params['is_separate'] = False
                    self.shoud_separate = False
                elif self.shoud_recogn:
                    # 需要识别时
                    # 分离成功后转为16k待识别音频
                    tools.conver_to_16k(self.init['vocal'], self.init['shibie_audio'])
        # 不分离，或分离失败
        if not self.config_params['is_separate']:
            try:
                self.status_text = config.transobj['kaishitiquyinpin']
                tools.split_audio_byraw(self.init['name'], self.init['source_wav'])
                # 需要识别
                if self.shoud_recogn:
                    tools.conver_to_16k(self.init['source_wav'], self.init['shibie_audio'])
            except Exception as e:
                raise Exception(
                    '从视频中提取声音失败，请检查视频中是否含有音轨，或该视频是否存在编码问题' if config.defaulelang == 'zh' else 'Failed to extract sound from video, please check if the video contains an audio track or if there is an encoding problem with that video')
        self.status_text = config.transobj['endfenliyinpin']
        return True


    # 配音预处理，去掉无效字符，整理开始时间
    def _before_tts(self):
        queue_tts = []
        # 获取字幕
        try:
            subs = tools.get_subtitle_from_srt(self.init['target_sub'])
            if len(subs) < 1:
                raise Exception("字幕格式不正确，请打开查看")
        except Exception as e:
            raise LogExcept(e)
        rate = int(str(self.config_params['voice_rate']).replace('%', ''))
        if rate >= 0:
            rate = f"+{rate}%"
        else:
            rate = f"{rate}%"
        # 取出设置的每行角色
        line_roles = self.config_params["line_roles"] if "line_roles" in self.config_params else None
        # 取出每一条字幕，行号\n开始时间 --> 结束时间\n内容
        for i, it in enumerate(subs):
            # 判断是否存在单独设置的行角色，如果不存在则使用全局
            voice_role = self.config_params['voice_role']
            if line_roles and f'{it["line"]}' in line_roles:
                voice_role = line_roles[f'{it["line"]}']
            newrole = voice_role.replace('/', '-').replace('\\', '/')
            filename = f'{i}-{newrole}-{self.config_params["voice_rate"]}-{self.config_params["voice_autorate"]}-{it["text"]}-{self.config_params["volume"].replace("%", "")}-{self.config_params["pitch"]}'
            # 要保存到的文件
            # clone-voice同时也是音色复制源
            filename = self.init['cache_folder'] + "/" + tools.get_md5(filename) + ".mp3"
            # 如果是clone-voice类型， 需要截取对应片段
            if it['end_time'] <= it['start_time']:
                continue
            # 是克隆
            if self.config_params['tts_type'] in ['clone-voice', 'CosyVoice'] and voice_role == 'clone':
                if self.config_params['is_separate'] and not tools.vail_file(self.init['vocal']):
                    raise Exception(f"背景分离出错 {self.init['vocal']}")
                    # clone 方式文件为wav格式
                if tools.vail_file(self.init['source_wav']):
                    tools.cut_from_audio(
                        audio_file=self.init['vocal'] if self.config_params[
                            'is_separate'] else self.init['source_wav'],
                        ss=it['startraw'],
                        to=it['endraw'],
                        out_file=filename
                    )

            queue_tts.append({
                "text": it['text'],
                "role": voice_role,
                "start_time": it['start_time'],
                "end_time": it['end_time'],
                "rate": rate,
                "startraw": it['startraw'],
                "endraw": it['endraw'],
                "volume": self.config_params['volume'],
                "pitch": self.config_params['pitch'],
                "tts_type": self.config_params['tts_type'],
                "filename": filename})
        self.queue_tts = queue_tts

    # 执行配音操作
    def _exec_tts(self):
        if not self.queue_tts or len(self.queue_tts) < 1:
            raise Exception(f'Queue tts length is 0')
        # 具体配音操作
        run_tts(
                queue_tts=copy.deepcopy(self.queue_tts),
                language=self.init['target_language_code'],
                uuid=self.uuid,
                inst=self
        )
        # 获取 novoice_mp4的长度
        if not tools.is_novoice_mp4(self.init['novoice_mp4'], self.init['noextname']):
            raise LogExcept("not novoice mp4")

    # 延长 novoice.mp4  duration_ms 毫秒
    def _novoicemp4_add_time(self, duration_ms):
        if duration_ms < 1000 or config.current_status!='ing':
            return

        self._signal(text=f'{config.transobj["shipinmoweiyanchang"]} {duration_ms}ms')
        if not tools.is_novoice_mp4(self.init['novoice_mp4'], self.init['noextname'], uuid=self.uuid):
            raise LogExcept("not novoice mp4")

        video_time = tools.get_video_duration(self.init['novoice_mp4'])
        shutil.copy2(self.init['novoice_mp4'], self.init['novoice_mp4'] + ".raw.mp4")
        try:

            tools.cut_from_video(
                source=self.init['novoice_mp4'],
                ss=tools.ms_to_time_string(ms=video_time - 100).replace(',', '.'),
                pts='20',
                out=self.init['cache_folder'] + "/last-clip-novoicepts20.mp4"
            )
            video_time2 = tools.get_video_duration(self.init['cache_folder'] + "/last-clip-novoicepts20.mp4")
            tools.cut_from_video(
                source=self.init['cache_folder'] + "/last-clip-novoicepts20.mp4",
                ss=tools.ms_to_time_string(ms=video_time2 - 100).replace(',', '.'),
                out=self.init['cache_folder'] + "/last-clip-novoice.mp4"
            )
            tools.runffmpeg([
                '-y',
                '-stream_loop',
                f'{math.ceil(duration_ms / 100)}',
                '-i',
                self.init['cache_folder'] + "/last-clip-novoice.mp4",
                '-c:v',
                'copy',
                '-an',
                self.init['cache_folder'] + "/last-clip-novoice-all.mp4"
            ])
        except Exception as  e:
            config.logger.exception(e,exc_info=True)

        tools.runffmpeg([
            '-y',
            '-i',
            f"{self.init['novoice_mp4']}.raw.mp4",
            '-i',
            self.init['cache_folder'] + "/last-clip-novoice-all.mp4",
            '-filter_complex',
            "[0:v][1:v]concat=n=2:v=1[outv]",
            '-map',
            "[outv]",
            '-an',
            self.init['novoice_mp4']])

        Path(f"{self.init['novoice_mp4']}.raw.mp4").unlink(missing_ok=True)
        return True

    # 添加背景音乐
    def _back_music(self):
        if self._exit():
            return
        if self.shoud_dubbing and tools.vail_file(self.init['target_wav']) and tools.vail_file(
                self.init['background_music']):
            try:
                self.status_text = '添加背景音频' if config.defaulelang == 'zh' else 'Adding background audio'
                # 获取视频长度
                vtime = tools.get_video_info(self.init['novoice_mp4'], video_time=True)
                vtime /= 1000
                # 获取音频长度
                atime = tools.get_audio_time(self.init['background_music'])

                # 转为m4a
                bgm_file = self.init['cache_folder'] + f'/bgm_file.m4a'
                if not self.init['background_music'].lower().endswith('.m4a'):
                    tools.wav2m4a(self.init['background_music'], bgm_file)
                    self.init['background_music'] = bgm_file
                else:
                    shutil.copy2(self.init['background_music'], bgm_file)
                    self.init['background_music'] = bgm_file

                beishu = math.ceil(vtime / atime)
                if config.settings['loop_backaudio'] and beishu > 1 and vtime - 1 > atime:
                    # 获取延长片段
                    file_list = [self.init['background_music'] for n in range(beishu + 1)]
                    concat_txt = self.init['cache_folder'] + f'/{time.time()}.txt'
                    tools.create_concat_txt(file_list, concat_txt=concat_txt)
                    tools.concat_multi_audio(
                        concat_txt=concat_txt,
                        out=self.init['cache_folder'] + "/bgm_file_extend.m4a")
                    self.init['background_music'] = self.init['cache_folder'] + "/bgm_file_extend.m4a"
                # 背景音频降低音量
                tools.runffmpeg(
                    ['-y', '-i', self.init['background_music'], "-filter:a",
                     f"volume={config.settings['backaudio_volume']}",
                     '-c:a', 'aac',
                     self.init['cache_folder'] + f"/bgm_file_extend_volume.m4a"])
                # 背景音频和配音合并
                cmd = ['-y', '-i', self.init['target_wav'], '-i',
                       self.init['cache_folder'] + f"/bgm_file_extend_volume.m4a",
                       '-filter_complex', "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2", '-ac', '2',
                       self.init['cache_folder'] + f"/lastend.m4a"]
                tools.runffmpeg(cmd)
                self.init['target_wav'] = self.init['cache_folder'] + f"/lastend.m4a"
            except Exception as e:
                config.logger.exception(f'添加背景音乐失败:{str(e)}',exc_info=True)

    def _separate(self):
        if self._exit():
            return
        if self.shoud_separate and tools.vail_file(self.init['target_wav']):
            try:
                self.status_text = '重新嵌入背景音' if config.defaulelang == 'zh' else 'Re-embedded background sounds'
                # 原始背景音乐 wav,和配音后的文件m4a合并
                # 获取视频长度
                vtime = tools.get_video_info(self.init['novoice_mp4'], video_time=True)
                vtime /= 1000
                # 获取音频长度
                atime = tools.get_audio_time(self.init['instrument'])
                beishu = math.ceil(vtime / atime)
                instrument_file = self.init['cache_folder'] + f'/instrument.wav'
                shutil.copy2(self.init['instrument'], instrument_file)
                self.init['instrument'] = instrument_file
                config.logger.info(f'合并背景音 {beishu=},{atime=},{vtime=}')
                if config.settings['loop_backaudio'] and atime + 1 < vtime:
                    # 背景音连接延长片段
                    file_list = [instrument_file for n in range(beishu + 1)]
                    concat_txt = self.init['cache_folder'] + f'/{time.time()}.txt'
                    tools.create_concat_txt(file_list, concat_txt=concat_txt)
                    tools.concat_multi_audio(concat_txt=concat_txt,
                                             out=self.init['cache_folder'] + "/instrument-concat.m4a")
                    self.init['instrument'] = self.init['cache_folder'] + f"/instrument-concat.m4a"
                # 背景音合并配音
                tools.backandvocal(self.init['instrument'], self.init['target_wav'])
            except Exception as e:
                config.logger.exception('合并原始背景失败' + config.transobj['Error merging background and dubbing'] + str(e),exc_info=True)



    # 处理所需字幕
    def _process_subtitles(self):
        if not self.init['target_sub'] or not Path(self.init['target_sub']).exists():
            raise LogExcept(f'不存在有效的字幕文件' if config.defaulelang == 'zh' else 'No valid subtitle file exists')

        # 如果原始语言和目标语言相同，或不存原始语言字幕，则强制单字幕
        if (self.init['source_language_code'] == self.init['target_language_code']) or (
                not self.init['source_sub'] or not Path(self.init['source_sub']).exists()):
            if self.config_params['subtitle_type'] == 3:
                self.config_params['subtitle_type'] = 1
            elif self.config_params['subtitle_type'] == 4:
                self.config_params['subtitle_type'] = 2
        # 最终处理后需要嵌入视频的字幕
        process_end_subtitle = self.init['target_dir'] + f'/end.srt'
        # 硬字幕时单行字符数
        maxlen = int(
            config.settings['cjk_len'] if self.init['target_language_code'][:2] in ["zh", "ja", "jp", "ko"] else
            config.settings['other_len'])
        target_sub_list = tools.get_subtitle_from_srt(self.init['target_sub'])

        # 双硬 双软字幕组装
        if self.config_params['subtitle_type'] in [3, 4]:
            maxlen_source = int(
                config.settings['cjk_len'] if self.init['source_language_code'][:2] in ["zh", "ja", "jp", "ko"] else
                config.settings['other_len'])
            source_sub_list = tools.get_subtitle_from_srt(self.init['source_sub'])
            source_length = len(source_sub_list)

            srt_string = ""
            for i, it in enumerate(target_sub_list):
                # 硬字幕换行，软字幕无需处理
                tmp = textwrap.fill(it['text'].strip(), maxlen, replace_whitespace=False) if self.config_params[
                                                                                                 'subtitle_type'] == 3 else \
                it['text'].strip()
                srt_string += f"{it['line']}\n{it['time']}\n{tmp}"
                if source_length > 0 and i < source_length:
                    srt_string += "\n" + (
                        textwrap.fill(source_sub_list[i]['text'], maxlen_source, replace_whitespace=False).strip() if
                        self.config_params['subtitle_type'] == 3 else source_sub_list[i]['text'])
                srt_string += "\n\n"
            Path(f"{self.init['target_dir']}/shuang.srt").write_text(srt_string.strip(), encoding='utf-8')
            process_end_subtitle = f"{self.init['target_dir']}/shuang.srt"
        elif self.config_params['subtitle_type'] == 1:
            # 单硬字幕，需处理字符数换行
            srt_string = ""
            for i, it in enumerate(target_sub_list):
                tmp = textwrap.fill(it['text'].strip(), maxlen, replace_whitespace=False)
                srt_string += f"{it['line']}\n{it['time']}\n{tmp.strip()}\n\n"
            Path(process_end_subtitle).write_text(srt_string, encoding='utf-8')
        else:
            # 单软字幕
            process_end_subtitle = self.init['target_sub']

        # 目标字幕语言
        subtitle_langcode = translator.get_subtitle_code(show_target=self.config_params['target_language'])

        # 单软 或双软
        if self.config_params['subtitle_type'] in [2, 4]:
            return os.path.basename(process_end_subtitle), subtitle_langcode

        # 硬字幕转为ass格式 并设置样式
        process_end_subtitle_ass = tools.set_ass_font(process_end_subtitle)
        Path(process_end_subtitle).unlink(missing_ok=True)
        return os.path.basename(process_end_subtitle_ass), subtitle_langcode

    # 延长视频末尾对齐声音
    def _append_video(self):
        # 有配音 延长视频或音频对齐
        if not self.shoud_dubbing or not self.config_params['append_video']:
            return
        video_time = tools.get_video_duration(self.init['novoice_mp4'])
        try:
            audio_length = int(tools.get_audio_time(self.init['target_wav']) * 1000)
        except Exception:
            audio_length = 0
        if audio_length > 0 and audio_length > video_time:
            try:
                # 先对音频末尾移除静音
                tools.remove_silence_from_end(self.init['target_wav'], is_start=False)
                audio_length = int(tools.get_audio_time(self.init['target_wav']) * 1000)
            except Exception:
                audio_length = 0
        if audio_length > 0 and audio_length > video_time:
            # 视频末尾延长
            try:
                # 对视频末尾定格延长
                self.status_text = '视频末尾延长中' if config.defaulelang == 'zh' else 'Extension at the end of the video'
                self._novoicemp4_add_time(audio_length - video_time)
            except Exception as e:
                config.logger.exception(f'视频末尾延长失败:{str(e)}', exc_info=True)
        elif audio_length > 0 and video_time > audio_length:
            ext = self.init['target_wav'].split('.')[-1]
            m = AudioSegment.from_file(
                self.init['target_wav'],
                format="mp4" if ext == 'm4a' else ext) + AudioSegment.silent(
                duration=video_time - audio_length)
            m.export(self.init['target_wav'], format="mp4" if ext == 'm4a' else ext)

    # 最终合成视频 source_mp4=原始mp4视频文件，noextname=无扩展名的视频文件名字
    def _compos_video(self):
        if self._exit():
            return
        if not self.shoud_hebing:
            return True
        # 判断novoice_mp4是否完成
        if not tools.is_novoice_mp4(self.init['novoice_mp4'], self.init['noextname']):
            raise LogExcept(config.transobj['fenlinoviceerror'])

        # 需要配音但没有配音文件
        if self.shoud_dubbing and not tools.vail_file(self.init['target_wav']):
            raise LogExcept(f"{config.transobj['Dubbing']}{config.transobj['anerror']}:{self.init['target_wav']}")

        subtitles_file, subtitle_langcode = None, None
        if self.config_params['subtitle_type'] > 0:
            subtitles_file, subtitle_langcode = self._process_subtitles()

        self.precent = 90 if self.precent < 90 else self.precent
        # 有配音 延长视频或音频对齐
        self._append_video()
        # 添加背景音乐
        self._back_music()
        # 重新嵌入分离出的背景音
        self._separate()

        self.precent = 95 if self.precent < 95 else self.precent

        protxt = config.TEMP_DIR + f"/compose{time.time()}.txt"
        threading.Thread(target=self.hebing_pro,args=(protxt,)).start()

        # 字幕嵌入时进入视频目录下
        os.chdir(Path(self.init['novoice_mp4']).parent.resolve())
        try:
            self.status_text = '视频+字幕+配音合并中' if config.defaulelang == 'zh' else 'Video + Subtitles + Dubbing in merge'
            # 有配音有字幕
            if self.config_params['voice_role'] != 'No' and self.config_params['subtitle_type'] > 0:
                if self.config_params['subtitle_type'] in [1, 3]:
                    self._signal(text=config.transobj['peiyin-yingzimu'])
                    # 需要配音+硬字幕
                    tools.runffmpeg([
                        "-y",
                        "-progress",
                        protxt,
                        "-i",
                        self.init['novoice_mp4'],
                        "-i",
                        Path(self.init['target_wav']).as_posix(),
                        "-c:v",
                        f"libx{self.video_codec}",
                        "-c:a",
                        "aac",
                        "-vf",
                        f"subtitles={subtitles_file}",
                        '-crf',
                        f'{config.settings["crf"]}',
                        '-preset',
                        config.settings['preset'],
                        Path(self.init['targetdir_mp4']).as_posix()
                    ])
                else:
                    # 配音+软字幕
                    self._signal(text=config.transobj['peiyin-ruanzimu'])
                    tools.runffmpeg([
                        "-y",
                        "-progress",
                        protxt,
                        "-i",
                        self.init['novoice_mp4'],
                        "-i",
                        Path(self.init['target_wav']).as_posix(),
                        "-i",
                        subtitles_file,
                        "-c:v",
                        "copy",
                        "-c:a",
                        "aac",
                        "-c:s",
                        "mov_text",
                        "-metadata:s:s:0",
                        f"language={subtitle_langcode}",
                        Path(self.init['targetdir_mp4']).as_posix()
                    ])
            elif self.config_params['voice_role'] != 'No':
                # 有配音无字幕
                self._signal(text=config.transobj['onlypeiyin'])
                tools.runffmpeg([
                    "-y",
                    "-progress",
                    protxt,
                    "-i",
                    self.init['novoice_mp4'],
                    "-i",
                    Path(self.init['target_wav']).as_posix(),
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    Path(self.init['targetdir_mp4']).as_posix()
                ])
            # 硬字幕无配音  原始 wav 合并
            elif self.config_params['subtitle_type'] in [1, 3]:
                self._signal(text=config.transobj['onlyyingzimu'])
                cmd = [
                    "-y",
                    "-progress",
                    protxt,
                    "-i",
                    self.init['novoice_mp4']
                ]
                if tools.vail_file(self.init['source_wav']):
                    cmd.append('-i')
                    cmd.append(Path(self.init['source_wav']).as_posix())

                cmd.append('-c:v')
                cmd.append(f'libx{self.video_codec}')
                if tools.vail_file(self.init['source_wav']):
                    cmd.append('-c:a')
                    cmd.append('aac')
                cmd += [
                    "-vf",
                    f"subtitles={subtitles_file}",
                    '-crf',
                    f'{config.settings["crf"]}',
                    '-preset',
                    config.settings['preset'],
                    Path(self.init['targetdir_mp4']).as_posix(),
                ]
                tools.runffmpeg(cmd)
            elif self.config_params['subtitle_type'] in [2, 4]:
                # 无配音软字幕
                self._signal(text=config.transobj['onlyruanzimu'])
                # 原视频
                cmd = [
                    "-y",
                    "-progress",
                    protxt,
                    "-i",
                    self.init['novoice_mp4']
                ]
                # 原配音流
                if tools.vail_file(self.init['source_wav']):
                    cmd.append("-i")
                    cmd.append(Path(self.init['source_wav']).as_posix())
                # 目标字幕流
                cmd += [
                    "-i",
                    subtitles_file,
                    "-c:v",
                    "copy"
                ]
                if tools.vail_file(self.init['source_wav']):
                    cmd.append('-c:a')
                    cmd.append('aac')
                cmd += [
                    "-c:s",
                    "mov_text",
                    "-metadata:s:s:0",
                    f"language={subtitle_langcode}",
                    '-crf',
                    f'{config.settings["crf"]}',
                    '-preset',
                    config.settings['preset']
                ]
                cmd.append(Path(self.init['targetdir_mp4']).as_posix())
                tools.runffmpeg(cmd)
        except Exception as e:
            msg=f'最后一步字幕配音嵌入时出错:{e}' if config.defaulelang=='zh' else f'Error in embedding the final step of the subtitle dubbing:{e}'
            self._signal(text=msg,type='error')
            raise LogExcept(msg)
        self.precent = 99
        os.chdir(config.ROOT_DIR)
        self._create_txt()
        self.precent = 100
        time.sleep(1)
        self.hasend=True
        return True

    # ffmpeg进度日志
    def hebing_pro(self,protxt):
        basenum = 100 - self.precent
        video_time = tools.get_video_duration(self.init['novoice_mp4'])
        while 1:
            if self.precent >= 100:
                return
            if not os.path.exists(protxt):
                time.sleep(1)
                continue
            with open(protxt, 'r', encoding='utf-8') as f:
                content = f.read().strip().split("\n")
                if content[-1] == 'progress=end':
                    return
                idx = len(content) - 1
                end_time = "00:00:00"
                while idx > 0:
                    if content[idx].startswith('out_time='):
                        end_time = content[idx].split('=')[1].strip()
                        break
                    idx -= 1
                try:
                    h, m, s = end_time.split(':')
                except Exception:
                    time.sleep(1)
                    continue
                else:
                    h, m, s = end_time.split(':')
                    precent = round((int(h) * 3600000 + int(m) * 60000 + int(s[:2]) * 1000) * basenum / video_time,
                                    2)
                    if self.precent + precent < 99.9:
                        self.precent += precent
                    self._signal(text='')
                    time.sleep(1)

    # 创建说明txt
    def _create_txt(self):
        try:
            Path(self.init['novoice_mp4']).unlink(missing_ok=True)
            if not self.config_params['only_video']:
                with open(self.init['target_dir'] + f'/{"readme" if config.defaulelang != "zh" else "文件说明"}.txt', 'w', encoding="utf-8", errors="ignore") as f:
                    f.write(f"""以下是可能生成的全部文件, 根据执行时配置的选项不同, 某些文件可能不会生成, 之所以生成这些文件和素材，是为了方便有需要的用户, 进一步使用其他软件进行处理, 而不必再进行语音导出、音视频分离、字幕识别等重复工作

        *.mp4 = 最终完成的目标视频文件
        {self.init['source_language_code']}.m4a|.wav = 原始视频中的音频文件(包含所有背景音和人声)
        {self.init['target_language_code']}.m4a = 配音后的音频文件(若选择了保留背景音乐则已混入)
        {self.init['source_language_code']}.srt = 原始视频中根据声音识别出的字幕文件
        {self.init['target_language_code']}.srt = 翻译为目标语言后字幕文件
        shuang.srt = 双语字幕
        vocal.wav = 原始视频中分离出的人声音频文件
        instrument.wav = 原始视频中分离出的背景音乐音频文件


        如果觉得该项目对你有价值，并希望该项目能一直稳定持续维护，欢迎各位小额赞助，有了一定资金支持，我将能够持续投入更多时间和精力
        捐助地址：https://github.com/jianchang512/pyvideotrans/issues/80

        ====

        Here are the descriptions of all possible files that might exist. Depending on the configuration options when executing, some files may not be generated.

        *.mp4 = The final completed target video file
        {self.init['source_language_code']}.m4a|.wav = The audio file in the original video (containing all sounds)
        {self.init['target_language_code']}.m4a = The dubbed audio file (if you choose to keep the background music, it is already mixed in)
        {self.init['source_language_code']}.srt = Subtitles recognized in the original video
        {self.init['target_language_code']}.srt = Subtitles translated into the target language
        shuang.srt = Source language and target language subtitles srt 
        vocal.wav = The vocal audio file separated from the original video
        instrument.wav = The background music audio file separated from the original video


        If you feel that this project is valuable to you and hope that it can be maintained consistently, we welcome small sponsorships. With some financial support, I will be able to continue to invest more time and energy
        Donation address: https://ko-fi.com/jianchang512


        ====

        Github: https://github.com/jianchang512/pyvideotrans
        Docs: https://pyvideotrans.com

                        """)
                if self.config_params['subtitle_type'] in [1, 3]:
                    Path(self.init['target_dir'] + f'/{subtitles_file}').unlink(missing_ok=True)
        except:
            pass