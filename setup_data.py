from main import pull, FILEINFO
from process_adv import run as process
import ttmlean

if __name__ == '__main__':
    pull(FILEINFO.values())

    process(FILEINFO.values())

    ttmlean.process(FILEINFO['ttm02b-top'])
