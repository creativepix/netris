# netris

Скомпилированная программа (запускать с гпу. ГПУ доступна, если есть галочка "Использовать гпу"): https://drive.google.com/file/d/1EZy3ohIMFci4fZKkZGWMjYJWFZrqi5x7/view?usp=sharing

Если у вас не установлен video codec (в этом случае видео не будет читаться), то рекоммендуется установить KLite: https://codecguide.com/download_k-lite_codec_pack_basic.htm

Запускать dist/main/run.exe

Формат выходного json:

[

&nbsp;{

&nbsp;&nbsp;"id": <id события>, 

&nbsp;&nbsp;"cls": <класс обьекта>, 

&nbsp;&nbsp;"start_timestamp": <начало события>, 

&nbsp;&nbsp;"end_timestamp": <конец события>, 

&nbsp;&nbsp;"possibility": <вероятность от 0 до 1>, "

&nbsp;&nbsp;center": [<X центра относящегося обьекта>, <Y центра относящегося обьекта>]
  
&nbsp;},

...

]
