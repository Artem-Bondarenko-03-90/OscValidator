import os
import re
import time
from datetime import datetime

from oscill import oscillogram
from validator import validator
import requests
import zipfile
from pathlib import Path
import json
import uuid


#метод загрузки осциллограммы на сервер конвертора


def send_osc(url , my_token, file_name_ls):
   headers = {'accept': 'text/plain', 'Authorization': my_token}
   files_ls = {}
   multiple_files = []
   for file_name in file_name_ls:
      fp = open(file_name, 'rb')
      files_ls[str(uuid.uuid4())] = fp
      multiple_files.append(('files', (fp)))

   response = requests.post(url=url, files=multiple_files, data={'externalIds': list(files_ls.keys())}, headers=headers)

   #закроем все открытые файлы
   for f in files_ls.values():
      f.close()
   if response.status_code == 200:
      return response.content
   else:
      return b''

#метод получения информации о загруженной осциллограмме
def get_conversion_status(url, files_ls, my_token):
   headers = {'accept': 'text/plain', 'Authorization': my_token, 'Content-Type': 'application/json'}
   response = requests.post(url=url, headers=headers, data=files_ls)
   return response.json()

#загрузка преобразованного файла comtrade
def get_converted_file(url, file_id, my_token, file_name, src_dir):
   headers = {'accept': 'application/zip', 'Authorization': my_token}
   response = requests.post(url=url, headers=headers, params={'fileDumpId': file_id})
   with open(file_name + '.zip', "wb") as code:
      code.write(response.content)
   z = zipfile.ZipFile(file_name + '.zip', 'r')
   z.extractall(path=src_dir)
   return response.status_code

def all_actions_with_api(domen, token, file_name_ls, current_dir):
   time_st=datetime.now()

   url1 = domen +'/convertertocomtrade/add-files'
   url2 = domen +'/convertertocomtrade/get-conversion-status'
   url3 = domen +'/convertertocomtrade/get-converted-file'

   success_dumps = []

   # отправляем файл в конвертор
   sended_files_ls = send_osc(url1, token, file_name_ls)

   if sended_files_ls != b'':
      status = 'Queue'
      i=0

      while status == 'Queue':
         dumps = get_conversion_status(url2, sended_files_ls, token)
         for dump in dumps:
            if dump['dumpFile']['status'] == 'Queue':
               time.sleep(5)  # ждем 5 с до следующей попытки запросить статус
               i+=1
               print('Wait '+str(i*5)+' seconds...')
               status = 'Queue'
               break
            else:
               status = 'NoQueue'
      time_wisout_download = datetime.now()
      count_dumps_all=0
      count_dumps_success = 0
      for dump in get_conversion_status(url2, sended_files_ls, token):
         if str(dump['dumpFile']['extension']).lower() in ('.aura', '.os1', '.os2', '.os3', '.bb', '.do', '.to'):
            count_dumps_all+=1
         if dump['dumpFile']['status'] == 'ConvertSuccess':
            if str(dump['dumpFile']['extension']).lower() in ('.aura', '.os1', '.os2', '.os3', '.bb', '.do', '.to'):
               count_dumps_success+=1
               print("Download file: "+dump['dumpFile']['fileNameWithoutExtension']+dump['dumpFile']['extension'])
               get_converted_file(url3, dump['dumpFile']['id'], token, current_dir+str(Path(dump['dumpFile']['fileNameWithoutExtension']).with_suffix('')), current_dir)
               success_dumps.append(dump)
         else:
            print("Convert unsuccess: Status - "+ dump['dumpFile']['status'])
      print('Количество отправленных на конвертацию файлов осциллограмм: '+ str(count_dumps_all))
      print('Количество успешно сконвертированных файлов осциллограмм: ' + str(count_dumps_success))
      print('Процент успешной конвертации: '+ str((count_dumps_success/count_dumps_all)*100)+'%')
      time_end = datetime.now()
      print('Общее время конвертации: '+str(time_end-time_st))
      print('Время конвертации без учёта загрузки comtrade: ' + str(time_wisout_download - time_st))
      return success_dumps
   else:
      print('Error: Don`t get dumpFile_list')




if __name__ == '__main__':

   ext_charset_map = {'.aura': '1251', '.os1': '866', '.os2': '866',
                      '.os3': '866', '.bb': '1251', '.to': '866', '.do': '866'}

   with open('settings.json') as f:
      settings_file = json.load(f)


   domain = settings_file['domain']
   token = settings_file['token']
   current_dir = settings_file['current_dir'].encode('utf-8').decode('utf-8')
   report_f = open(current_dir + 'report.txt', 'w')
   validator = validator()

   dir_path = current_dir

   src_file_ls = []
   for dirs in list(os.walk(dir_path)):
      for file in dirs[2]:
         suf = str(Path(file).suffix).lower()
         if suf in ['.aura', '.bb', '.brs', '.dfr', '.os1', '.os2', '.os3', '.osc', '.sg2'] or re.fullmatch('.[td][0o][\S]', suf) or re.fullmatch('.[td][0o]', suf):
            st = (dirs[0]+'\\'+file).replace('\\', '/')
            src_file_ls.append(st)
   success_dumps=all_actions_with_api( domain, token, src_file_ls, current_dir)
   # валидация
   if success_dumps != None:
      for dump in success_dumps:
         if dump['dumpFile']['extension'] in ['.aura', '.bb', '.brs', '.dfr', '.os1', '.os2', '.os3', '.osc', '.sg2'] or re.fullmatch('.[td][0o]', str(dump['dumpFile']['extension']).lower()):
            st3 = str(current_dir + dump['dumpFile']['fileNameWithoutExtension']+'.cfg').replace(',', '.')
            f = open(st3, 'r', encoding=ext_charset_map[str(dump['dumpFile']['extension']).lower()])
            osc = oscillogram(f)
            validator.osc = osc
            #добавляем файл dat только в том случае если он существует
            if validator.dat_file_is_exist():
               osc.set_data_file()
            report_f.write('Расширение исходного файла: ' + str(dump['dumpFile']['extension']) + ';\n')
            validator.full_oscillogram_validation(report_f)
            osc.close_dat_file()
            f.close()
   report_f.close()

   msg = str(input('Для завершения нажмите пробел'))

