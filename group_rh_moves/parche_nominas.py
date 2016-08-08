# Este script le pone el codigo alpha 3 a los paises, para ejecutar:
# python parche_paises_sat.py <nombre_bd>
import pycountry
import psycopg2
import sys

# Cambiar esta linea si se requiere un usuario o password diferente

dbname = "offset_pruebas"
conn = psycopg2.connect("dbname=%s user=openerpoisa password=Zentella1 host=localhost"%dbname) 

cr = conn.cursor()
cr2 = conn.cursor()
cr3 = conn.cursor()
cr.execute("select id,name from hr_payslip_run")
for row in cr.fetchall():
    print row[0]
    cr2.execute("select id, name,payslip_run_id, move_id from hr_payslip where payslip_run_id = %s and move_id is not Null"%(row[0]))
    for row2 in cr2.fetchall():
        print row2[3]
#        cr3.execute("update account_move set nomina_id='%s',slip_id='%s' where id='%s' and nomina_id is Null"%(row[0],row2[0],row2[3]))
        cr3.execute("update account_move set nomina_id='%s',slip_id='%s' where id='%s' and (nomina_id is Null or slip_id is Null)"%(row[0],row2[0],row2[3]))
    
conn.commit()
conn.close()
print "terminado"
