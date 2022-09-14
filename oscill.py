import os


class oscillogram(object):

    def __init__(self, cfg_file = None):
        self.cfg_file = cfg_file

    #метод добавления dat файла
    def set_data_file(self):
        dat_path = self.cfg_file.name
        dat_path = dat_path[:len(dat_path) - 3] + 'dat'
        dat_f = open(dat_path, 'r')
        self.dat_file = dat_f

    #метод закрытия dat файла
    def close_dat_file(self):
        try:
            self.dat_file.close()
        except AttributeError:
            pass


    #получение строки по номеру из cfg файла
    def get_cfg_string(self, number):
        self.cfg_file.seek(0)
        try:
            return str(self.cfg_file.readlines()[int(number)-1]).rstrip()
        except IndexError:
            return ''

    #получение ревизии comtrade
    def get_comtrade_revision(self):
        rev=''
        try:
            rev=self.get_cfg_string(1).split(',')[2]
        except IndexError:
            rev = '1991'
        if rev == '':
            rev = '1991'

        return rev


    #получение общего количества сигналов
    def get_total_count_signals(self):
        return str(self.get_cfg_string(2).split(',')[0])

    #получение количества аналоговых сигналов
    def get_count_analog_signals(self):
        res=str(self.get_cfg_string(2).split(',')[1])
        return res[:len(res)-1]

    #получение количества дискретных сигналов
    def get_count_digital_signals(self):
        res = str(self.get_cfg_string(2).split(',')[2])
        return res[:len(res) - 1]

    #получение номинальной частоты сети
    def get_nominal_frequency(self):
        return str(self.get_cfg_string(int(self.get_total_count_signals())+3))

    #получение количества частот дискретизации
    def get_count_rates(self):
        return str(self.get_cfg_string(int(self.get_total_count_signals())+4))

    #получение списка частот дискретизации
    def get_samps_ls(self):
        res = []
        n = int(self.get_total_count_signals())+5
        for i in range(int(self.get_count_rates())):
            res.append(str(self.get_cfg_string(n+i).split(',')[0]))
        return res

    # получение списка номеров последних выборок
    def get_last_samps_number_ls(self):
        res = []
        n = int(self.get_total_count_signals()) + 5
        for i in range(int(self.get_count_rates())):
            res.append(str(self.get_cfg_string(n + i).split(',')[1]))
        return res

    #получение максимального номера выборки
    def get_max_samp_number(self):
        res=[]
        n = int(self.get_total_count_signals())+5
        for i in range(int(self.get_count_rates())):
            res.append(int(self.get_cfg_string(n+i).split(',')[1]))
        return max(res)

    #получение даты старта записи
    def get_date_start(self):
        n=int(self.get_total_count_signals())+int(self.get_count_rates())+5
        return str(self.get_cfg_string(n).split(',')[0])

    #получение времени старта записи
    def get_time_start(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 5
        return str(self.get_cfg_string(n).split(',')[1])

    # получение даты пуска
    def get_date_trig(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 6
        return str(self.get_cfg_string(n).split(',')[0])

    # получение времени старта
    def get_time_trig(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 6
        return str(self.get_cfg_string(n).split(',')[1])

    #получение типа dat файла
    def get_dat_file_type(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 7
        return str(self.get_cfg_string(n))

    # получение коэффициента для умножения временных меток
    def get_timemult(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 8
        return str(self.get_cfg_string(n))

    #получение time_code (только для ревизии comtrade 2013)
    def get_time_code_rev2013(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 9
        return str(self.get_cfg_string(n).split(',')[0])

    # получение local_code (только для ревизии comtrade 2013)
    def get_local_code_rev2013(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 9
        return str(self.get_cfg_string(n).split(',')[1])

    #получение кода качества синхронизации внутренних часов осциллографа (только для ревизии comtrade 2013)
    def get_time_quality_code_rev2013(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 10
        return str(self.get_cfg_string(n).split(',')[0])

    #получить показатель корректировочной секунды
    def get_leap_sec_rev2013(self):
        n = int(self.get_total_count_signals()) + int(self.get_count_rates()) + 10
        return str(self.get_cfg_string(n).split(',')[1])

    #получить размер файла в байтах
    def get_file_size_b(self, file):
        file.seek(0, os.SEEK_END )
        return int(file.tell())

    # получить размер файла в строках
    def get_file_size_str(self, file):
        line_count = 0
        for line in file:
            line_count += 1
        return line_count

