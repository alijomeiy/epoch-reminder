import jdatetime

my_dict = {}

start_date = jdatetime.date.today()

for i in range(120):
    current_date = start_date + jdatetime.timedelta(days=i)
    date_str = current_date.strftime('%Y/%m/%d')
    my_dict[date_str] = i + 1

for k, v in list(my_dict.items())[:5]:
    print(f"{k} : {v}")
