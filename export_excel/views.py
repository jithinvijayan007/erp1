import pandas as pd
from pandas import ExcelWriter
from django.conf import settings
from POS import ins_logger
from datetime import datetime,timedelta
# Create your views here.
def get_col_widths(dataframe):
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

def export_excel(typeofreport,all,from_date,to_date,table_data):
    try:
        india_offset = timedelta(hours=5,minutes=30)
        today = datetime.today() + india_offset
        strTitle = str(typeofreport).title()+' Report '
        datFrom = str(from_date)[0:10]
        datTo = str(to_date)[0:10]
        filename = strTitle.replace(' ','_')+datFrom+'_to_'+datTo+'.xlsx'
        #path_name = settings.STATIC_DIR+"/"+filename
        path_name = settings.MEDIA_ROOT+"/"+filename
        writer = ExcelWriter(path_name,engine='xlsxwriter')
        workbook = writer.book
        bold_clm = workbook.add_format({'bold':True,'font_size':13})
        clm = workbook.add_format({'font_size':13})
        rw = workbook.add_format({'border':True,'font_size':12})
        bold_title = workbook.add_format({'bold':True,'font_size':30})
        border = workbook.add_format({'border':True})
        worksheet = workbook.add_worksheet()
        worksheet.hide_gridlines(2)
        writer.sheets['Sheet1'] = worksheet
        header = table_data[0].keys()
        data_list = table_data
        df = pd.DataFrame(data_list,columns=header)
        df.index += 1
        df.index.name = 'Sl No.'
        df.to_excel(writer,'Sheet1',index=True,startrow=8)
        if not df.shape[1]%2:
            int_mid = df.shape[1]/2
        else:
            int_mid = (df.shape[1]-1)/2
        workbook.add_format({'border':True})
        worksheet.write(3,1,'From',clm)
        worksheet.write(3,2,datFrom,bold_clm)
        worksheet.write(4,1,'To',clm)
        worksheet.write(4,2,datTo,bold_clm)

        lst_types = ['service', 'productivity']
        if typeofreport.lower() in lst_types and 'branch' in all:
            worksheet.write(5,1,'Branch',clm)
            worksheet.write(5,2,table_data[0]['Branch'],bold_clm)
        if typeofreport.lower() in lst_types and 'staff' in all:
            if 'all' in all:
                worksheet.write(6,7,'Staff',clm)
                worksheet.write(6,8,table_data[0]['Staff Name'],bold_clm)
            else:
                worksheet.write(6,6,'Staff',clm)
                worksheet.write(6,7,table_data[0]['Staff Name'],bold_clm)
        worksheet.set_zoom(90)
        worksheet.set_row(1,50)
        worksheet.set_row(8,None,rw)
        for row_no in range(9,df.shape[0]+9):
            worksheet.set_row(row_no,None,border)
        worksheet.write(1,int_mid,strTitle,bold_title)
        worksheet.write(3,df.shape[1],str(all).title(),bold_clm)
        worksheet.write(3,df.shape[1]-1,str(typeofreport).title(),clm)
        if typeofreport.lower() in lst_types and 'all' in all:
            worksheet.write(3,df.shape[1],str('All').title(),bold_clm)
        elif typeofreport.lower() in lst_types:
            worksheet.write(3,df.shape[1],str(all.split('+')[0]).title(),bold_clm)
        else:
            worksheet.write(3,df.shape[1],str(all).title(),bold_clm)
        if typeofreport == 'new customer':
            worksheet.write(3,df.shape[1]-1,'Branch',clm)
        elif typeofreport == 'Customer Feedback':
            lst_datas = all.split(',')
            worksheet.write(3,df.shape[1]-1,'Branch',clm)
            worksheet.write(3,df.shape[1],str(lst_datas[0]).title(),bold_clm)
            worksheet.write(5,1,'Staff',clm)
            worksheet.write(5,2,str(lst_datas[1]).title(),bold_clm)

        elif typeofreport == 'source':
            lst_datas = all.split(',')
            worksheet.write(3,df.shape[1]-1,'Branch',clm)
            worksheet.write(3,df.shape[1],str(lst_datas[0]).title(),bold_clm)
            worksheet.write(5,1,'Source',clm)
            worksheet.write(5,2,str(lst_datas[1]).title(),bold_clm)
        elif typeofreport == 'airline':
            lst_datas = all.split('-')
            worksheet.write(3,df.shape[1]-1,'Branch',clm)
            worksheet.write(3,df.shape[1],str(lst_datas[0]).title(),bold_clm)
            worksheet.write(5,1,'airline',clm)
            worksheet.write(5,2,str(lst_datas[1]).title(),bold_clm)
        elif typeofreport =='mobile source':
            lst_datas = all.split('-')
            worksheet.write(3,df.shape[1]-1,'Branch',clm)
            worksheet.write(3,df.shape[1],str(lst_datas[0]).title(),bold_clm)
            worksheet.write(5,1,'Source',clm)
            worksheet.write(5,2,str(lst_datas[1]).title(),bold_clm)
        else:
            worksheet.write(3,df.shape[1]-1,str(typeofreport).title(),clm)

        worksheet.write(4,df.shape[1]-1,'Report Date',clm)
        worksheet.write(4,df.shape[1],today.strftime('%d-%m-%Y'),bold_clm)
        worksheet.write(5,df.shape[1]-1,'Report Time',clm)
        worksheet.write(5,df.shape[1],datetime.now().strftime('%I:%M:%S %p'),bold_clm)
        for i, width in enumerate(get_col_widths(df)):
            worksheet.set_column(i, i, width)
        writer.save()
        #return settings.HOSTNAME+"/static/"+filename
        return settings.HOSTNAME+"/media/"+filename
    except Exception as e:
        ins_logger.logger.error(str(e))
        return False
