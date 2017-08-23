import re


RE_SECONDS = re.compile(r' E[^C][-+]?[0-9]*\.?[0-9]+s')
RE_SECONDS_REACHED = re.compile(r' E[^C][-+]?[0-9]*\.?[0-9]+')
RE_NUM_THREADS = re.compile(r'Threads\s+:\s*(.*)')
RE_DECK = re.compile(r'Input\s+:\s*(.*)')
RE_RUN_TYPE = re.compile(r'Run Type\s+:\s*(.*)')
RE_NUM_PROCESES = re.compile(r'Parallel with (\d+) processes')
RE_RUN_TIME = re.compile(r'Simulation complete.*[=]')
RE_RUN_TIME_REACHED = re.compile(r'The simulation has reached(.*?)s')
RE_RUN_TIME_START = re.compile(r'Starting the simulation(.*?)s')
RE_RUN_TIME_DEF = re.compile(r'Processing model definitions(.*?)s')


def parse(re_compiled, string_prt, call_me_with_m, what):
    m = re_compiled.findall(string_prt)
    if m:
        try:
            return call_me_with_m(m)
        except:
            raise IOError('Could not parse ' + what)
    raise IOError('Could not find ' + what)


def parse_deck_name(string_prt):
    def _parse(m):
        return m[0].replace('.afi', '')
    return parse(RE_DECK, string_prt, _parse, 'deck name')


def parse_num_threads(string_prt):
    def _parse(m):
        return int(m[0])
    try:
        return parse(RE_NUM_THREADS, string_prt, _parse, 'thread count')
    except:
        return 1 # default if not in prt


def parse_reported_start_time(string_prt):
    def _parse(m):
        string_time = RE_SECONDS_REACHED.findall(m[-1])
        return int(float(string_time[0][2:]))
    return parse(RE_RUN_TIME_START, string_prt, _parse, 'simulation start time')


def parse_reported_definitions_time(string_prt):
    def _parse(m):
        string_time = RE_SECONDS_REACHED.findall(m[-1])
        return int(float(string_time[0][2:]))
    return parse(RE_RUN_TIME_DEF, string_prt, _parse, 'definitions elapsed time')


def parse_last_reported_run_time(string_prt):
    def _parse(m):
        string_time = RE_SECONDS_REACHED.findall(m[-1])
        return int(float(string_time[0][2:]))
    return parse(RE_RUN_TIME_REACHED, string_prt, _parse, 'last reported run time')


def parse_run_time(string_prt):
    def _parse(m):
        string_time = RE_SECONDS.findall(m[0])
        return int(float(string_time[0][2:-1]))
    try:
        return parse(RE_RUN_TIME, string_prt, _parse, 'run time')
    except:
        # bail out, some models have a cut off gold prt
        try:
            return parse_last_reported_run_time(string_prt)
        except:
            # and again if no simulation sectino reports
            try:
                return parse_reported_start_time(string_prt)
            except:
                # and definitions only
                return parse_reported_definitions_time(string_prt)
            


def parse_num_processes(string_prt):
    def _parse(m):
        num_processes = 1 # 'serial'
        m = RE_NUM_PROCESES.match(m[0])
        if m:
            num_processes = int(m.group(1))
        return num_processes
    return parse(RE_RUN_TYPE, string_prt, _parse, 'process count')