#!/usr/bin/python
###Antes de compilar el archivo hay que eliminar el SUB que se encuentra en ellos###
import os
def Space(vMin,vMax): #Genera una cadena con puros espacios
	cad=""
	while vMin<vMax: #Numero de espacios a generar
		cad+=" "
		vMin+=1
	return cad #De esta manera no se extiende el codigo al escribir los espacios explicitamente

def NumSpa(l): #Cuenta el numero de espacios que hay entre dos cadenas. La cadena no debe tener espacios en los costados
	i=l.find(" ") #Indice del primer espacio en blanco en la cadena
	cont=0
	while l[i]==" ":
		i+=1
		cont+=1
	return cont #Si no hay espacios, la unica posibilidad es que sea una etiqueta de referencia o un nemonico Inherente

def Separaciones(l): #Cuenta cuantas veces hay una separacion entre dos cadenas diferentes.Ejem: RESET FCB #$8000
	cont=0
	ini=l.find(" ")
	if l.find(" ",ini+NumSpa(l),len(l)) != -1:
		cont+=1
	return cont #Al igual que NumSpa nos puede indicar si es una etiqueta de referencia

def Directivas(name): #Guarda en una cadena el nombre de la variable y su valor asociado cada vez que encuentra la palabra EQU
	DE=""
	f=open(name,"r")
	l=f.readline().strip() #No debe contener espacios a los costados

	while l!="":
		if "EQU" in l:
			lim=l.find(" ",l.find("EQU"),len(l)) #Primer ocurrencia de lo que estamos buscando apartir de un rango
			etiqueta=l[lim:].strip()
			if lim == -1:
				etiqueta="ERROR: No hay separacion entre la directiva EQU y el valor correspondiente"
			DE+=l[0:l.find(" ")]+"|"+"$"+Convierte(etiqueta)+"|"
		l=f.readline()
	return DE #Estructura de la cadena: nombre|valorOriginal|

def isHexa(numHexa): #Verifica si es un numero hexadecimal
	hexa="0123456789abcdefABCDEF"
	i=0
	band=True

	while i<len(numHexa):
		if numHexa[i] not in hexa:
			band=False
		i+=1

	return band

def Convierte(val): #Si se requiere convierte la etiqueta a su respectiva equivalencia hexadecimal
	if "#" in val:
		val=val.replace("#","") #Quitamos este simbolo de la etiqueta
	if val.strip().find(" ") != -1: #Ejem: $00,X,#$80 C1. Saltos
		p1=Convierte(val[0:val.find(",")])
		aux=val[::-1] #Volteamos la cadena 1C 08$#,X,00$
		p2=aux[aux.find(" ")+NumSpa(aux):aux.find(",")] #Obtenemos el segundo valor de manera mas facil
		p2=Convierte(p2[::-1]) #Volvemos a voltear la cadena para que regrese a su forma normal y lo filtramos
		val=p1+p2
		salto=aux[0:aux.find(" ")]
		val=p1+p2+"|"+salto[::-1] #Solo quedan los valores sin basura
		return val
	elif "," in val: #Ejem: $00,X,#$40 o linea con FCB
		p1=Convierte(val[0:val.find(",")])
		p2=""
		if val.count(",") == 2: #Caso normal
			aux=val[::-1] #Volteamos la cadena 04$#,X,00$
			p2=aux[0:aux.find(",")] #Obtenemos el segundo valor de manera mas facil
			p2=Convierte(p2[::-1]) #Volvemos a voltear la cadena para que regrese a su forma normal y lo filtramos
		val=p1+p2
		if isHexa(val) == False:
			return "ERROR:"+val+" no es un valor hexadecimal"
		return val
	elif "$" in val: #Forzozamente la direccion de memoria asosiada esta en hexadecimal
		val=val[1:]
		if len(val)>=1 and len(val)<=4: #Rango permitido
			if isHexa(val) == False:
				return "ERROR:"+val+" no es un valor hexadecimal"
			return Acompleta(val)
		return "ERROR:"+val+"no es un valor permitido"
	elif "'" in val: #Es un caracter
		val=val[val.find("'")+1:]
		if len(val) == 1: #No podemos cargar una palabra si fuera asi entonces EQU no sirviria de nada
			val=Acompleta(hex(ord(val))).upper() #Convertimos en hexadecimal el valor ASSCI del caracter
			return val
		return "ERROR:"+val+"No es un caracter permitido"
	else: #El valor esta en decimal o es un nombre que no tienen un valor aosciado
		if val.isdigit(): #Como el valor es decimal no es posible que haya letras
			return Acompleta(hex(int(val))).upper()
		return "0" #Es posible que haya que convertir algun nombre y eso no es posible

def Acompleta(val): #Para tener solamente longitudes pares
	if "0x" in val: #Al convertir de decimal a hexadecimal el formato es el siguiente 0xFFFF
		val=val[2:]
	if len(val) == 1:
		return "0"+val
	elif len(val) == 3:
		val="0"+val
		if val[0:2] == "00":
			val=val[2:]
		return val
	elif len(val) == 4:
		if val[0:2] == "00":
			val=val[2:]
		return val
	else:
		return val #len(val) = 2

def Mnemonico(l): #Divide la linea actual (sin espacios en los costados) en dos variables: Mnemonico y Etiqueta
	if l.find(" ") == -1:
		return l+"|"+" "+"&"+" " #Si no hay espacios entre dos cadenas la unica posibilidad es que sea una etiqueta de referencia
	elif "RESET" in l: #Ejem: RESET FCB $80,$00
		lim=l.find(" ")
		nemonico=l[lim+NumSpa(l):l.find(" ",lim+NumSpa(l),len(l))]
		etiqueta=l[l.find(" ",lim+NumSpa(l),len(l))+NumSpa(l):].strip()
		ref=l[0:l.find(" ")]
		return nemonico+"|"+etiqueta+"&"+ref
	else:
		nemonico=l[0:l.find(" ")]
		etiqueta=l[len(nemonico)+NumSpa(l):]
		return nemonico+"|"+etiqueta+"&"+" "

def EtiEsp(ES): #Se crea una etiqueta especial
	if "#" in ES:
		ES=ES.replace("#","")
	if "$" in ES:
		return ES
	elif ES.isdigit():
		return ES
	elif "'" in ES:
		return ES
	else: #Etiqueta especial (var o cte)
		lim=DE.find("|",DE.find(ES),len(DE))
		return DE[lim+1:DE.find("|",lim+1,len(DE))]

def Pasada1(f):
	l=f.readline()
	MemoSalt={}
	
	while l!="":
		salt=l[24:l.find("|",25,len(l))].strip()
		eta=l[52:l.find(" ",53,len(l))].strip()
		nco=l[44:l.find("|",45,len(l))].strip()
		l=l[0:69]
		memodir=l[7:11].strip()

		if salt != "" and l.find("*")==-1 and l.find("EQU")==-1 and memodir.find(" ")==-1 and salt!="RESET":
			MemoSalt[salt]=memodir

		l=f.readline()
	return MemoSalt

def Complemento(cad,ban1):
	i=0
	numC2=""

	while i<len(cad):
		if ban1 == True: #Si encontramos el primer 1 lo que sigue es complementar
			numC2+=cad[i]
			if cad[i] == "1":
				ban1=False #Lo que sigue se tiene que complementar
		else:
			numC2+=str(int(cad[i])^1) #Hace el complemento
		i+=1

	return numC2

def Comp2(numHex): #Regresa el negativo de un numero hexadecimal dado. El valor como parametro no es una cadena
	bandPos=False
	if numHex>0:
		bandPos=True
	aux=bin(int(str(abs(numHex)),16)) #Regresa Numero Binario
	aux=aux[2:] #Quitamos el prefijo
	i=len(aux)

	while i<8:
		aux="0"+aux
		i+=1

	numC2=Complemento(aux[::-1],True) #Pasamos la cadena invertida

	if bandPos==True:
		numC2=Complemento(numC2,True)
		p1=numC2[0:4]
		p2=numC2[4:]
		aux=str(int(p2[::-1],2))+str(int(p1[::-1],2))
		return aux #[2:]

	aux=hex(int(numC2[::-1],2)).upper()
	return aux[2:]

def CodEnd(nemonico,etiqueta,l,MemoSalt,memo,NumPasada): #Genera el codigo de acuerdo al modo de direccionamiento que pertenece el mnemonico
	INH="ABA|1B|ABX|3A|ABY|183A|ASLA|48|ASLB|58|ASLD|5|ASRA|47|ASRB|57|CBA|11|CLC|0C|CLI|0E|CLRA|4F|CLRB|5F|CLV|0A|COMA|43|COMB|53|DAA|19|DECA|4A|DECB|5A|DES|34|DEX|09|DEY|1809|FDIV|03|IDIV|02|INCA|4C|INCB|5C|INS|31|INX|08|INY|1808|LSLA|48|LSLB|58|LSLD|05|LSRA|44|LSRB|54|LSRD|04|MUL|3D|NEGA|40|NEGB|50|NOP|01|PSHA|36|PSHB|37|PSHX|3C|PSHY|183C|PULA|32|PULB|33|PULX|38|PULY|1838|ROLA|49|ROLB|59|RORA|46|RORB|56|RTI|3B|RTS|39|SBA|10|SEC|0D|SEI|0F|SEV|0B|STOP|CF|SWI|3F|TAB|16|TAP|06|TBA|17|TETS|00|TPA|07|TSTA|4D|TSTB|5D|TSX|30|TSY|1830|TXS|35|TYS|1835|WAI|3E|XGDX|8F|XGDY|188F|"
	INDY="ADCA|18A9|ADCB|18E9|ADDA|18AB|ADDB|18EB|ADDD|18E3|ANDA|18A4|ANDB|18E4|ASL|1868|ASR|1867|BCLR|181D|BITA|18A5|BITB|18E5|BRCLR|181F|BRSET|181E|BSET|181C|CLR|186F|CMPA|18A1|CMPB|18E1|COM|1863|CPD|CDA3|CPX|CDAC|CPY|18AC|DEC|186A|EORA|18A8|EORB|18E8|INC|186C|JMP|186E|JSR|18AD|LDAA|18A6|LDAB|18E6|LDD|18EC|LDS|18AE|LDX|CDEE|LDY|18EE|LSL|1868|LSR|1864|NEG|1860|ORAA|18AA|ORAB|18EA|ROL|1869|ROR|1866|SBCA|18A2|SBCB|18E2|STAA|18A7|STAB|18E7|STD|18ED|STS|18AF|STX|CDEF|STY|18EF|SUBA|18A0|SUBB|18E0|SUBD|18A3|TST|186D|"
	INDX="ADCA|A9|ADCB|E9|ADDA|AB|ADDB|EB|ADDD|E3|ANDA|B4|ANDB|E4|ASL|68|ASR|67|BCLR|1D|BITA|A5|BITB|E5|BRCLR|1F|BRSET|1E|BSET|1C|CLR|6F|CMPA|A1|CMPB|E1|COM|63|CPD|1AA3|CPX|AC|CPY|18AC|DEC|6A|EORA|A8|EORB|E8|INC|6C|JMP|6E|JSR|AD|LDAA|A6|LDAB|E6|LDD|EC|LDS|AE|LDX|EE|LDY|18EE|LSL|68|LSR|64|NEG|60|ORAA|AA|ORAB|EA|ROL|69|ROR|66|SBCA|A2|SBCB|E2|STAA|A7|STAB|E7|STD|ED|STS|AF|STX|EF|STY|1AEF|SUBA|A0|SUBB|E0|SUBD|A3|TST|6D|"
	EXT="ADCA|B9|ADCB|F9|ADDA|BB|ADDB|FB|ADDD|F3|ANDA|B4|ANDB|F4|ASL|78|ASR|77|BITA|B5|BITB|F5|CLR|7F|CMPA|B1|CMPB|F1|COM|73|CPD|1AB3|CPX|BC|CPY|18BC|DEC|7A|EORA|B8|EORB|F8|INC|7C|JMP|7E|JSR|BD|LDAA|B6|LDAB|F6|LDD|FC|LDS|BE|LDX|FE|LDY|18FE|LSL|78|LSR|74|NEG|70|ORAA|BA|ORAB|FA|ROL|79|ROR|76|SBCA|B2|SBCB|F2|STAA|B7|STAB|F7|STD|FD|STS|BF|STX|FF|STY|18FF|SUBA|B0|SUBB|F0|SUBD|B3|TST|7D|"
	DIR="ADCA|99|ADCB|D9|ADDA|9B|ADDB|DB|ADDD|D3|ANDA|94|ANDB|D4|BCLR|15|BITA|95|BITB|D5|BRCLR|13|BRSET|12|BSET|14|CMPA|91|CMPB|D1|CPD|1A93|CPX|9C|CPY|189C|EORA|98|EORB|D8|JSR|9D|LDAA|96|LDAB|D6|LDD|DC|LDS|9E|LDX|DE|LDY|18DE|ORAA|9A|ORAB|DA|SBCA|92|SBCB|D2|STAA|97|STAB|D7|STD|DD|STS|9F|STX|DF|STY|18DF|SUBA|90|SUBB|D0|SUBD|93|"
	IMM="ADCA|89|ADCB|C9|ADDA|8B|ADDB|CB|ADDD|C3|ANDA|84|ANDB|C4|BITA|85|BITB|C5|CMPA|81|CMPB|C1|CPD|1A83|CPX|8C|CPY|188C|EORA|88|EORB|C8|LDAA|86|LDAB|C6|LDD|CC|LDS|8E|LDX|CE|LDY|18CE|ORAA|8A|ORAB|CA|SBCA|82|SBCB|C2|SUBA|80|SUBB|C0|SUBD|83|"
	REL="BCC|24|BCS|25|BEQ|27|BGE|2C|BGT|2E|BHI|22|BHS|24|BLE|2F|BLO|25|BLS|23|BLT|2D|BMI|2B|BNE|26|BPL|2A|BRA|20|BRN|21|BSR|8D|BVC|28|BVS|29|"
	Bifurcacion="BCC|BCS|BEQ|BGE|BGT|BHI|BHS|BLE|BLO|BLS|BLT|BMI|BNE|BPL|BRA|BRCLR|BRN|BRSET|BSR|BVC|BVS|JMP|JSR|RTI|RTS|"

	lon=len(Convierte(EtiEsp(etiqueta)))

	if l[0]==" ":
		if "FCB" == nemonico:
			p1=Convierte(EtiEsp(etiqueta[0:etiqueta.find(",")])) #quite strip
			p2=Convierte(EtiEsp(etiqueta[etiqueta.find(",")+1:])) #quite strip
			if len(p1)==2 and len(p2)==2:
				return "0"+"|"+p1+p2+"&"
			return "0"+"|"+"La direccion "+p1+p2+" no es valida"+"&"
		elif "END" == nemonico:
			return "5"+"|"+"  "+"&"
		elif "," in etiqueta:
			aux=0
			limit=INDX.find("|",INDX.find(nemonico),len(INDX))
			CodIns=INDX[limit+1:INDX.find("|",limit+1,len(INDX))]
			if "Y" in etiqueta:
				limit=INDY.find("|",INDY.find(nemonico),len(INDY))
				CodIns=INDY[limit+1:INDY.find("|",limit+1,len(INDY))]
			valaux=Convierte(EtiEsp(etiqueta))
			val=valaux
			bandera=False
			if "|" in valaux:
				val=valaux[0:valaux.find("|")]
				bandera=True
			if bandera == True:
				aux+=2
				if NumPasada == 2:
					saltarA=valaux[valaux.find("|")+1:]
					val+=Comp2(int(MemoSalt[saltarA],16)-int(memo,16)-len(CodIns)-2)
					aux=len(CodIns)+len(val)
					return str((aux)/2)+"|"+CodIns+val+"&"
			aux+=len(CodIns)+len(val)
			return str((aux)/2)+"|"+CodIns+val+"&"
		elif nemonico=="JSR" or nemonico=="JMP":
			limit=EXT.find("|",EXT.find(nemonico),len(EXT))
			aux="ZZZZ"
			if NumPasada == 2:
				aux="ERROR: No se ha encontrado "+etiqueta
				if etiqueta in MemoSalt:
					aux=MemoSalt[etiqueta]
				return str((len(aux)+2)/2)+"|"+EXT[limit+1:EXT.find("|",limit+1,len(EXT))]+aux+"&"
			return str((len(aux)+2)/2)+"|"+EXT[limit+1:EXT.find("|",limit+1,len(EXT))]+aux+"&"
		elif "#" in etiqueta : #Modo Inmediato
			val=Convierte(EtiEsp(etiqueta[etiqueta.find("#")+1:]))
			if "00" in etiqueta[1:4] : #Entrea: #$00FF Devuelve: FF
				val=etiqueta[etiqueta.find("0"):]
			if "X" in nemonico and len(val)==2: #Ya que la etiqueta debe de ser de 16 bits
				val="00"+val
			limit=IMM.find("|",IMM.find(nemonico),len(IMM))
			aux=len(IMM[limit+1:IMM.find("|",limit+1,len(IMM))]+val)
			return str(aux/2)+"|"+IMM[limit+1:IMM.find("|",limit+1,len(IMM))]+val+"&"
		elif lon == 2: #Modo Directo
			val=Convierte(EtiEsp(etiqueta))
			if nemonico=="CLR": #Ya que el nemonico se llega a confundir con otros similares al modo DIR
				val="00"+val
				limit=EXT.find("|",EXT.find(nemonico),len(EXT))
				aux=len(EXT[limit+1:EXT.find("|",limit+1,len(EXT))]+val) #Hay que checar lo que pasa cuando esta mal escrita la var o cte. Si str(0) seria un error
				return str(aux/2)+"|"+EXT[limit+1:EXT.find("|",limit+1,len(EXT))]+val+"&"
			limit=DIR.find("|",DIR.find(nemonico),len(DIR))
			aux=len(DIR[limit+1:DIR.find("|",limit+1,len(DIR))]+val)
			return str(aux/2)+"|"+DIR[limit+1:DIR.find("|",limit+1,len(DIR))]+val+"&"
		elif lon == 4 : #Modo Extendido
			val=Convierte(EtiEsp(etiqueta))
			limit=EXT.find("|",EXT.find(nemonico),len(EXT))
			aux=len(EXT[limit+1:EXT.find("|",limit+1,len(EXT))]+val) #Hay que checar lo que pasa cuando esta mal escrita la var o cte. Si str(0) seria un error
			return str(aux/2)+"|"+EXT[limit+1:EXT.find("|",limit+1,len(EXT))]+val+"&"
		elif nemonico in INH: #Modo Inherente
			limit=INH.find("|",INH.find(nemonico),len(INH))
			aux=len(INH[limit+1:INH.find("|",limit+1,len(INH))])
			return str(aux/2)+"|"+INH[limit+1:INH.find("|",limit+1,len(INH))]+"&"
		elif nemonico in REL: #Modo Relativo
			limit=REL.find("|",REL.find(nemonico),len(REL))
			val="ZZ"
			if NumPasada == 2:
				val=Comp2(int(MemoSalt[etiqueta],16)-int(memo,16)-len(REL[limit+1:REL.find("|",limit+1,len(REL))]))
			aux=len(REL[limit+1:REL.find("|",limit+1,len(REL))])+len(val)
			return str((aux)/2)+"|"+REL[limit+1:REL.find("|",limit+1,len(REL))]+val+"&"
		else: #La unica posibilidad es que la etiqueta sea una referencia dentro del programa
			return "0|ERROR:"+nemonico+" no es un mnemonico valido&"
	elif l[0]!=" " and etiqueta==" " : #Necesariamente es una subrutina o un ciclo
		return "0"+"|"+" "+"&"
	else: #No se respeta la identacion
		if "RESET" in l: #Excepcion
			p1=Convierte(EtiEsp(etiqueta[0:etiqueta.find(",")])) #Quite strip
			p2=Convierte(EtiEsp(etiqueta[etiqueta.find(",")+1:])) #Quite strip
			if len(p1)==2 and len(p2)==2:
				return "0"+"|"+p1+p2+"&"
			return "0"+"|"+"La direccion "+p1+p2+" no es valida"+"&"
		return "0|ERROR:La identacion no esta bien gestionada&"

def WriteFile(f,name,l,cont,DE,memo,flag,MemoSalt,Pasada): #Escribe de manera recursiva un archivo .lst el resultado de la compilacion
	g=open(name+".lst","a")

	if l == "": #Se ha llegado al final del archivo que contiene el codigo fuente
		return "0" #Termina la recursion de la funcion

	elif l == "\n" or len(l.strip()) == 0: #La linea actual es un salto de linea o contiene puros espacios en blanco
		g.write(str(cont)+Space(len(str(cont)),5)+"|"+Space(0,6)+"| "+Space(0,8)+" |"+Space(0,18)+"|"+Space(0,7)+"|"+"\n")
		g.seek(2) #Indicamos que queremos escribir al final del archivo (con esto el archivo ya no se escribira al reves)
		cont+=1 #Numero de linea actual
		return WriteFile(f,name,f.readline(),cont,DE,memo,flag,MemoSalt,Pasada) #Al hacer recursiva la funcion el archivo se escribe al reves

	elif "EQU" in l: #La linea actual contiene la Directiva EQU
		if l[0] != " ":
			nom=l[0:l.find(" ")]
			lim=l.find(" ",l.find("EQU"),len(l)) #Primer ocurrencia de lo que estamos buscando apartir de un rango
			val=l[lim:].strip()
			g.write(str(cont)+Space(len(str(cont)),5)+"|"+Space(0,6)+"| "+Convierte(val)+Space(0,9-len(Convierte(val)))+"| "+nom+Space(0,17-len(nom))+"| EQU"+Space(0,3)+"| "+val+"\n")
			g.seek(2)
			cont+=1
			return WriteFile(f,name,f.readline(),cont,DE,memo,flag,MemoSalt,Pasada)
		g.write("Al usar la directiva EQU la linea no debe tener espacios en blanco al principio")
		g.seek(2)
		cont+=1
		return WriteFile(f,name,f.readline(),cont,DE,memo,flag,MemoSalt,Pasada)

	elif "*" == l[0]: #La linea actual sirve solo como referencia en el programa (tipo de presentacion en forma de comentario)			
		g.write(str(cont)+Space(len(str(cont)),5)+"|"+Space(0,6)+"| "+l[l.find("*"):len(l)])
		g.seek(2)
		cont+=1
		return WriteFile(f,name,f.readline(),cont,DE,memo,flag,MemoSalt,Pasada)

	else: #La linea actual contienen el codigo a compilar
		coment="\n"
		laux=l[0:l.find("\n")] #Linea sin comentarios
		if "*" in l: #La linea actual contiene comentarios. Separamos el comentario del codigo
			coment=l[l.find("*"):] #Contiene ya el salto de linea
			laux=l[0:l.find("*")]

		cad=Mnemonico(laux.strip()) #Linea sin espacios en blanco(en los bordes) ni salto de linea
		key=cad[0:cad.find("|")] #Mnemonico
		etiqta=cad[cad.find("|")+1:cad.find("&")] #Operando del mnemonico
		ref=cad[cad.find("&")+1:]

		res=CodEnd(key,etiqta,laux,MemoSalt,memo,Pasada) #Traduccion del mnemonico y de la etiqueta y alguna referencia
		cod=res[res.find("|")+1:res.find("&")] #Codigo del mnemonico y de su operando
		if Pasada == 2:
			print cod
		num=int(res[0:res.find("|")]) #Localidades de memoria ocupadas
		colum4=Space(0,18) #Espacios en blanco de la columna 4

		if "ORG" in l: #Cada vez que encontramos ORG la memoria se inicializa al valor asignado
			flag=True
			laux=laux.strip() #Linea sin espacios ni saltos de linea
			memo="0x"+Acompleta(Convierte(laux[laux.find(" ")+NumSpa(laux):])) #No importa que el valor sea decimal o hexadecimal
			cod="  "
			num=0

		if cod == " ": #La linea actual solo contiene una etiqueta de referencia
			colum4=key+Space(0,18-len(key)) #Hacemos que la etiqueta de referencia este en la columna 4
			key=etiqta=""

		if "ERROR" in cod:
			key=etiqta=""

		if "RESET" == ref:
			colum4=ref+Space(0,18-len(ref))

		cad=str(cont)+Space(len(str(cont)),5)+"|"+Space(0,5)+" | "+cod+Space(0,8-len(cod))+" |"+colum4+"| "+key+Space(0,5-len(key))+" | "+etiqta+Space(0,17-len(etiqta))+coment
		if flag == True and key!="END":
			cad=str(cont)+Space(len(str(cont)),5)+"| "+memo[2:len(memo)]+" | "+cod+Space(0,8-len(cod))+" |"+colum4+"| "+key+Space(0,5-len(key))+" | "+etiqta+Space(0,17-len(etiqta))+coment
			memo=hex(int(str(int(memo,16)+num))).upper()
			if int(memo,16) >= 65535:
				memo="0x0000"
		g.write(cad)
		g.seek(2)
		cont+=1
		return WriteFile(f,name,f.readline(),cont,DE,memo,flag,MemoSalt,Pasada)

print "\nCompilador basico del MC68HC11\t\n"
print "Creado por:\n\tGarcia Tobon Carlos\n\n"
name=raw_input("Escriba el nombre del archivo a compilar:\n")

try:
	f1=open(name,"r") #Archivo a compilar
	f2=open(name,"r") #No se porque no puedo ocupar el mismo archivo otra vez
		
	DE=Directivas(name) #Variables y Constantes
	MemoSalt=""
	cont=1 #Numero de linea
	memo="ZZZZ" #Valor de la memoria
	flag=False #Bandera de memoria para saber que localidad es el inicio
	
	WriteFile(f1,"aux",f1.readline(),cont,DE,memo,flag,MemoSalt,1)
	f3=open("aux.lst","r")
	MemoSalt=Pasada1(f3)
	os.remove(os.getcwd()+"/"+"aux.lst") #Borramos el archivo auxiliar

	WriteFile(f2,name[0:name.find(".")],f2.readline(),cont,DE,memo,flag,MemoSalt,2) #Se le da una segunda pasada
	
	print "\n\tEl programa fue compilado con exito\n"

except IOError:

	WriteLog("El archivo no existe en la ruta actual o en el directorio especificado")

finally:
	f1.close()
	f2.close()
