import os
import re
import time

from oscill import oscillogram
from validator import validator
import requests
import zipfile
from pathlib import Path
import json

#метод загрузки осциллограммы на сервер конвертора
def send_osc(url , my_token, f_path):
   #headers = {'accept': 'text/plain', 'Authorization': my_token, 'Content-Type': 'multipart/form-data;boundary=---boundary'}
   #headers = {'accept': 'text/plain', 'Authorization': my_token,'Content-Type': 'multipart/form-data'}
   headers = {'accept': 'text/plain', 'Authorization': my_token}
   with open(f_path, 'rb') as fp:
      #payload = MultipartEncoder({f_path: fp})
      response = requests.post(url=url, files={'content':fp}, headers=headers)
   if response.status_code == 200:
      #print(response.content.decode('utf-8').replace('"', ''))
      return response.content.decode('utf-8').replace('"', '')
   else:
      return ''

#метод получения информации о загруженной осциллограмме
def get_dump_file_result(url, file_id, my_token):
   #url = 'http://172.16.22.11:5025/convertertocomtrade/get-dump-file-result'
   headers = {'accept': 'text/plain', 'Authorization': my_token}
   response = requests.post(url=url, headers=headers, params={'fileDumpId': file_id})
   return response.json()#['dumpFile']['status']

#загрузка преобразованного файла comtrade
def get_convering_file(url, file_id, my_token, file_name):
   #url = 'http://172.16.22.11:5025/convertertocomtrade/get-convering-file'
   headers = {'accept': 'application/zip', 'Authorization': my_token}
   response = requests.post(url=url, headers=headers, params={'fileDumpId': file_id})
   #print(response.headers)
   with open(file_name + '.zip', "wb") as code:
      code.write(response.content)
   z = zipfile.ZipFile(file_name + '.zip', 'r')
   z.extractall(path=file_name)
   return response.status_code

def all_actions_with_api(domen, token, file_name:str):
   url1 = domen +'/convertertocomtrade/add-files'
   url2 = domen +'/convertertocomtrade/get-dump-file-result'
   url3 = domen +'/convertertocomtrade/get-convering-file'
   #http://172.16.22.11:5025
   file_name_without_ext = str(Path(file_name).with_suffix(''))
   # отправляем файл в конвертор
   dumpId = send_osc(url1, token, file_name)
   #print(dumpId)
   if dumpId != '':
      #n = 0
      #print(get_dump_file_result(url2, dumpId, token))
      status = get_dump_file_result(url2, dumpId, token)['dumpFile']['status']
      while status == 'Queue':
         #n+=1
         time.sleep(10) #ждем 10 с до следующей попытки запросить статус
         status = get_dump_file_result(url2, dumpId, token)['dumpFile']['status']
      if status not in ('ConvertSuccess', 'Queue'):
         return 'Error: Convert unsuccess: status - ' +status +' ; file_name: '+ file_name
      if get_convering_file(url3, dumpId, token, file_name_without_ext) == 200:
         return file_name
   return  'Error: Don`t get dumpId'


if __name__ == '__main__':

   with open('settings.json') as f:
      settings_file = json.load(f)


   domain = settings_file['domain']
   token = settings_file['token']
   current_dir = settings_file['current_dir'].encode('utf-8').decode('utf-8')
   report_f = open(current_dir + 'report.txt', 'w')
   validator = validator()

   dir_path = current_dir
   for dirs in list(os.walk(dir_path)):
      for file in dirs[2]:

         if str(Path(file).suffix).lower() in ['.aura', '.bb', '.brs', '.dfr', '.os1', '.os2', '.os3', '.osc', '.sg2']:
            print(Path(file).suffix.lower())
            st = (dirs[0]+'\\'+file).replace('\\', '/')
            print(all_actions_with_api( domain, token, st))

   # валидация
   for dirs in list(os.walk(dir_path)):
      for file in dirs[2]:
         st = (dirs[0]+'\\'+file).replace('\\', '/')
         if st[-3:] in ('cfg', 'CFG'):
            f = open(st, 'r')



            osc = oscillogram(f)
            validator.osc = osc

            #добавляем файл dat только в том случае если он существует
            if validator.dat_file_is_exist():
               osc.set_data_file()
            validator.full_oscillogram_validation(report_f)

            osc.close_dat_file()
            f.close()
   report_f.close()

