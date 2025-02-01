try:
    from typing import Callable, Optional
    import sys
    import datetime
    import colorama
    import tqdm
    from .typings import Finalise, Progress, Alert
except KeyboardInterrupt:
    raise SystemExit(1)

colorama.just_fix_windows_console()

def format_duration(remaining: int, prefix: str = '', suffix: str = '') -> str:
    duration = datetime.timedelta(seconds=remaining)
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3_600)
    minutes, seconds = divmod(remainder, 60)
    units = ''.join([
        f'{days}d' if days > 0 and days < 100000 else '',
        f'{hours}h' if hours > 0 and days < 100 else '',
        f'{minutes}m' if minutes > 0 and days == 0 else '',
        f'{seconds}s' if seconds > 0 and hours == 0 and days == 0 else ''
    ])
    if not units: return ''
    return prefix + units + suffix

class tqdm_custom(tqdm.tqdm):
    @property
    def format_dict(self):
        super_format_dict = super(tqdm_custom, self).format_dict
        complete = super_format_dict['n'] == super_format_dict['total']
        duration = format_duration(super_format_dict['elapsed'], prefix='took ') if complete else format_duration(super_format_dict['elapsed'], suffix=' left')
        dynamic_newline = ' ' if complete else '\n'
        super_format_dict.update(duration=duration, dynamic_newline=dynamic_newline)
        return super_format_dict

def setup(verbose: bool) -> tuple[Alert, Progress, Finalise]:
    def alert(message: str, *, importance: Optional[str] = None) -> None:
        if not importance and not verbose: return
        if importance == 'error': message = colorama.Style.BRIGHT + colorama.Fore.RED + message + colorama.Style.RESET_ALL
        if importance == 'warning': message = colorama.Style.BRIGHT + colorama.Fore.MAGENTA + message + colorama.Style.RESET_ALL
        sys.stderr.write(f'{message}\n')
    def progress(operation: str, total: int) -> Callable[[], None]:
        sys.stderr.write('\n')
        bar = tqdm_custom(desc=operation, total=total, bar_format='\x1b[F{desc: <30} |{bar}| {percentage:3.0f}% {duration: >11}{dynamic_newline}', dynamic_ncols=True)
        def update() -> None: bar.update()
        return update
    def finalise(mode: str, message: Optional[str] = None) -> None:
        if message: alert(message, importance='error')
        if mode == 'interrupt': sys.stderr.write('\rInterrupted!')
        elif mode == 'error': sys.stderr.write('\rFailed!')
        elif mode == 'complete': sys.stderr.write('Success!\n')
    return alert, progress, finalise
