import math
import os
import re
from typing import TextIO

from oscill import oscillogram

class validator(object):

    def __init__(self, osc:oscillogram = None):
        self.osc = osc

    #1 проверка наличия dat файла в той же папке что и cfg
    def dat_file_is_exist(self):
        dat_path = self.osc.cfg_file.name
        dat_path = dat_path[:len(dat_path) - 3] + 'dat'
        if os.path.exists(dat_path) and os.path.isfile(dat_path):
            return True
        return False

    #2 валидация 1 строки cfg
    def first_str_cfg_is_valid(self):
        rev = self.osc.get_comtrade_revision()
        if rev in ['1999', '2013']:
            if len(self.osc.get_cfg_string(1).split(',')) == 3:
                return True
            else:
                return False
        elif rev == '1991':
            if len(self.osc.get_cfg_string(1).split(',')) in (2, 3):
                return True
            else:
                return False
        else:
            return False


    #2 валидная или нет ревизия comtrade
    def revision_comtrade_is_valid(self):
        if self.osc.get_comtrade_revision() in ['1991', '1999', '2013']:
            return True
        return False

    #3 валидация второй строки cfg
    def second_str_cfg_is_valid(self):
        filds = self.osc.get_cfg_string(2).split(',')
        for f in filds:
            if f == '':
                return False
        if len(self.osc.get_cfg_string(2).split(',')) == 3:
            return True
        else:
            return False

    #4 валидация строк описания аналоговых каналов
    def a_signals_is_valid(self):
        rev = self.osc.get_comtrade_revision()
        type_dat_file = self.osc.get_dat_file_type()
        n = int(self.osc.get_count_analog_signals())
        for i in range(3,n+3):
            try:

                str_a_signal = self.osc.get_cfg_string(i).split(',')

                # номер сигнала
                if len(str_a_signal[0]) >= 1 and  len(str_a_signal[0]) <= 6:
                    try:
                        signal_number = int(str_a_signal[0])
                        if signal_number < 1 or signal_number > 999999:
                            return False
                    except ValueError:
                        return False
                else:
                    return False

                # наименование сигнала
                if rev != '2013':
                    if len(str_a_signal[1]) > 64:
                        return False
                else:
                    if len(str_a_signal[1]) > 64 or len(str_a_signal[1]) < 1:
                        return False

                # идентификатор фазы
                if len(str_a_signal[2]) > 2:
                    return False

                # присоединение
                if len(str_a_signal[3]) > 64:
                    return False

                # единицы измерения
                if len(str_a_signal[4]) > 64 or len(str_a_signal[4]) < 1:
                    return False

                # коэффициент модуля сигнала
                if len(str_a_signal[5]) <= 32 and len(str_a_signal[5]) >= 1:
                    try:
                        float(str_a_signal[5])
                    except ValueError:
                        return False
                else:
                    return False

                # коэффициент смещения
                if len(str_a_signal[6]) <= 32 and len(str_a_signal[6]) >= 1:
                    try:
                        float(str_a_signal[6])
                    except ValueError:
                        return False
                else:
                    return False

                # сдвиг времени канала относительно выборки
                if len(str_a_signal[7]) <= 32 and len(str_a_signal[7]) >= 1:
                    try:
                        float(str_a_signal[7])
                    except ValueError:
                        return False
                else:
                    return False

                # нижняя граница канала
                if type_dat_file in ['ASCII', 'ascii']:
                    if len(str_a_signal[8]) <= 6 and len(str_a_signal[8]) >= 1:
                        try:
                            if int(str_a_signal[8]) < -99999 or int(str_a_signal[8]) > 99999:
                                return False
                        except ValueError:
                            return False
                    else:
                        return False
                elif type_dat_file in ['BINARY', 'binary']:
                    if len(str_a_signal[8]) <= 6 and len(str_a_signal[8]) >= 1:
                        try:
                            if int(str_a_signal[8]) < -32767 or int(str_a_signal[8]) > 32767:
                                return False
                        except ValueError:
                            return False
                        pass
                    else:
                        return False

                # верхняя граница канала
                if type_dat_file in ['ASCII', 'ascii']:
                    if len(str_a_signal[9]) <= 6 and len(str_a_signal[9]) >= 1:
                        try:
                            if int(str_a_signal[9]) < -99999 or int(str_a_signal[9]) > 99999:
                                return False
                        except ValueError:
                            return False
                    else:
                        return False
                elif type_dat_file in ['BINARY', 'binary']:
                    if len(str_a_signal[9]) <= 6 and len(str_a_signal[9]) >= 1:
                        try:
                            if int(str_a_signal[9]) < -32767 or int(str_a_signal[9]) > 32767:
                                return False
                        except ValueError:
                            return False
                    else:
                        return False

                # первичная часть коэффициента трансформации
                if len(str_a_signal[10]) <= 32 and len(str_a_signal[10]) >= 1:
                    try:
                        float(str_a_signal[10])
                    except ValueError:
                        return False
                else:
                    return False

                # вторичная часть коэффициента трансформации
                if len(str_a_signal[11]) <= 32 and len(str_a_signal[11]) >= 1:
                    try:
                        float(str_a_signal[11])
                    except ValueError:
                        return False
                else:
                    return False

                # идентификатор первичные/вторичные величины
                if str_a_signal[12] not in ['p', 'P', 's', 'S']:
                    return False
            except IndexError:
                return False

        return True

    #5 валидация строк описания дискретных каналов
    def d_signals_is_valid(self):
        rev = self.osc.get_comtrade_revision()
        type_dat_file = self.osc.get_dat_file_type()
        n1 = int(self.osc.get_count_analog_signals())
        n2 = int(self.osc.get_count_digital_signals())
        for i in range(n1+3, n1+n2+3):
            try:
                str_d_signal = self.osc.get_cfg_string(i).split(',')

                # номер сигнала
                if len(str_d_signal[0]) >= 1 and len(str_d_signal[0]) <= 6:
                    try:
                        signal_number = int(str_d_signal[0])
                        if signal_number < 1 or signal_number > 999999:
                            return False
                    except ValueError:
                        return False
                else:
                    return False

                # наименование сигнала
                if rev != '2013':
                    if len(str_d_signal[1]) > 64:
                        return False
                else:
                    if len(str_d_signal[1]) > 64 or len(str_d_signal[1]) < 1:
                        return False

                # идентификатор фазы
                if len(str_d_signal[2]) > 2:
                    return False

                # присоединение
                if len(str_d_signal[3]) > 64:
                    return False

                # нормальное состояние дискретного сигнала
                if str_d_signal[4] not in ['0', '1']:
                    return False


            except IndexError:
                return False

        return True

    #6 валидация строки с номинальной частотой сети
    def frequency_str_is_valid(self):
        if len(self.osc.get_nominal_frequency()) <= 32:
            return True
        else:
            return False

    #7 валидация строки с количеством частот дискретизации
    def nrates_str_is_valid(self):
        n_rates = self.osc.get_count_rates()
        if len(n_rates) >= 1 and len(n_rates) <= 3:
            return True
        else:
            return False

    #8 валидация списка частот дискретизации
    def samps_is_valid(self):
        ls = self.osc.get_samps_ls()
        for samp in ls:
            if len(samp) < 1 or len(samp) > 32:
                return False
            else:
                try:
                    float(samp)
                except ValueError:
                    return False
        return True

    # 8 валидация списка номеров последних выборок
    def last_numer_samps_is_valid(self):
        ls = self.osc.get_last_samps_number_ls()
        for last_samp in ls:
            if len(last_samp) < 1 or len(last_samp) > 10:
                return False
            else:
                try:
                    if int(last_samp) < 1 or int(last_samp) > 9999999999:
                        return False
                except ValueError:
                    return False
        return True

    #9 валидация даты начала осциллограммы
    def start_date_is_valid(self):
        start_date = self.osc.get_date_start()
        if re.fullmatch('[0-3]\d/[0-1]\d/\d{4}', start_date):
            if int(start_date.split('/')[2]) > 1990 and int(start_date.split('/')[2]) < 9999:
                return True
        return False

    # 9 валидация времени начала осциллограммы
    def start_time_is_valid(self):
        start_time = self.osc.get_time_start()
        if re.fullmatch('[0-2]\d:[0-5]\d:[0-5]\d.\d{6}', start_time):
            return True
        return False

    # 9 валидация даты пуска осциллографа
    def trig_date_is_valid(self):
        trig_date = self.osc.get_date_trig()
        if re.fullmatch('[0-3]\d/[0-1]\d/\d{4}', trig_date):
            if int(trig_date.split('/')[2]) > 1990 and int(trig_date.split('/')[2]) < 9999:
                return True
        return False

    # 9 валидация времени пуска осциллографа
    def trig_time_is_valid(self):
        trig_time = self.osc.get_time_trig()
        if re.fullmatch('[0-2]\d:[0-5]\d:[0-5]\d.\d{6}', trig_time):
            return True
        return False

    # 10 валидация строки с типом dat файла
    def dat_file_type_is_valid(self):
        type = self.osc.get_dat_file_type()
        if type in ['BINARY', 'binary', 'ASCII', 'ascii']:
            return True
        return False

    #11 валидация строки с коэффициентом для умножения timestamp
    def timemult_is_valid(self):
        timemult=self.osc.get_timemult()
        if len(timemult) >= 1 and len(timemult) <= 32:
            try:
                float(timemult)
            except ValueError:
                return False
            return True
        return False

    #12 валидация строки содержащей time_code и local_code
    def tcode_and_lcode_is_valid(self):
        if self.osc.get_comtrade_revision() == '2013':
            time_code = self.osc.get_time_code_rev2013()
            if len(time_code) < 1 or len(time_code) >= 7:
                return False
            local_code = self.osc.get_local_code_rev2013()
            if len(time_code) < 1 or len(time_code) >= 7:
                return False
            return True

    #13 валидация строки содержащей показатель качества синхронизации времени и корректировочной секунды
    def tquality_and_leapsecond_is_valid(self):
        if self.osc.get_comtrade_revision() == '2013':
            time_quality = self.osc.get_time_quality_code_rev2013()
            if time_quality not in ['F', '4', '0']:
                return False
            leap_second = self.osc.get_leap_sec_rev2013()
            if leap_second not in ['3', '2', '1', '0']:
                return False
            return True

    # проверка количества строк в dat файле
    def count_string_in_dat_file_is_valid(self):
        try:
            osc_type = self.osc.get_dat_file_type()
            if osc_type in ['BINARY', 'binary']:
                b_in_string = 8 + int(self.osc.get_count_analog_signals())*2+math.ceil(int(self.osc.get_count_digital_signals())/16.0)*2
                b_in_file = int(self.osc.get_file_size_b(self.osc.dat_file))
                count_string_in_cfg = int(self.osc.get_max_samp_number())
                if b_in_file//b_in_string == count_string_in_cfg:
                    return True
                else:
                    return False
            elif osc_type in ['ASCII', 'ascii']:
                str_in_file = self.osc.get_file_size_str(self.osc.dat_file)
                count_string_in_cfg = int(self.osc.get_max_samp_number())
                if str_in_file == count_string_in_cfg:
                    return True
                else:
                    return False
        except AttributeError:
            return False

    # метод полной валидации осциллограммы
    def full_oscillogram_validation(self, report_file:TextIO):

        report_file.write(self.osc.cfg_file.name + '\n')
        report_file.write('*'*60+ '\n')
        report_file.write('dat файл найден: '+ ('OK;' if self.dat_file_is_exist() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация первой строки cfg файла: ' + ('OK;' if self.first_str_cfg_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Корректная ревизия comtrade cfg файла: ' + ('OK;' if self.revision_comtrade_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация второй строки cfg файла: ' + ('OK;' if self.second_str_cfg_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация описания аналоговых каналов cfg файла: ' + ('OK;' if self.a_signals_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация описания дискретных каналов cfg файла: ' + ('OK;' if self.d_signals_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация значения номинальной частоты сети cfg файла: ' + ('OK;' if self.frequency_str_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация количества частот дискретизации cfg файла: ' + ('OK;' if self.nrates_str_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация списка частот дискретизации cfg файла: ' + ('OK;' if self.samps_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация списка номеров последних выборок cfg файла: ' + ('OK;' if self.last_numer_samps_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация даты начала осциллограммы cfg файла: ' + ('OK;' if self.start_date_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация времени начала осциллограммы cfg файла: ' + ('OK;' if self.start_time_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация даты пуска осциллографа cfg файла: ' + ('OK;' if self.trig_date_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация времени пуска осциллографа cfg файла: ' + ('OK;' if self.trig_time_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация типа dat файла из cfg файла: ' + ('OK;' if self.dat_file_type_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация коэффициента умножения timestamp из cfg файла: ' + ('OK;' if self.timemult_is_valid() else 'ОШИБКА!') + '\n')
        if self.osc.get_comtrade_revision() == '2013':
            report_file.write('Валидация строки с time_code и local_code из cfg файла: ' + ('OK;' if self.tcode_and_lcode_is_valid() else 'ОШИБКА!') + '\n')
            report_file.write('Валидация строки с показателем качества синхронизации времени и корректировочной секунды из cfg файла: ' + ('OK;' if self.tquality_and_leapsecond_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('Валидация dat файла в части размера: ' + ('OK;' if self.count_string_in_dat_file_is_valid() else 'ОШИБКА!') + '\n')
        report_file.write('-' * 60 + '\n')
        report_file.write('\n')