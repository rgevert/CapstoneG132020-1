from datetime import date, datetime, timedelta, time
import matplotlib.pyplot as plt
from time import time as t

from entidades import Paciente, Evento, Atencion, AtencionExterna, AsignacionSemanal, Falla
from linkedlist import LinkedList
from random import randint, uniform, normalvariate, choice, seed as rseed
from parametros import *

#rseed(0)

class CentroKine:

    #INPUT recursos: list int, tiempo_inicio: datetime, tiempo_fin: datetime
    def __init__(self, tiempo_inicio, tiempo_fin, alpha):
        self.penalizaciones = 0
        self.schedule = []
        self.recursos = CANTIDAD_EQUIPO_PERSONAL_DISPONIBLE
        self.tiempo_inicio = tiempo_inicio
        self.tiempo_actual = tiempo_inicio
        self.tiempo_fin = tiempo_fin
        self.alpha = alpha
        self.externas = 0
        self.pacientes_atendiendose = [0 for i in range(9)]
        self.pacientes_diarios = [[] for i in range(10)]
        self.dias = []

        primer_evento = AsignacionSemanal(self.tiempo_actual- timedelta(seconds = 1))
        self.agregar_evento(primer_evento)
        self.agregar_evento(Falla(self.tiempo_actual + timedelta(days = 4), self.tiempo_actual + timedelta(days = 4) + timedelta(hours = 7), [5,0,0,0,0,0]))

        #ATRIBUTOS PARA ESTADISTICAS
        self.pacientes_listos = []
        self.pacientes_aceptados = 0
        self.pacientes_rechazados = 0

    def agregar_evento(self, evento):

        """AGREGA UN NUEVO EVENTO AL SCHEDULE
           Y LA ORDENA SEGUN TIEMPO DE INICIO """

        self.schedule.append(evento)
        self.schedule.sort(key=lambda evento: evento.inicio)

    def asignacion_semanal(self, pacientes):
        #Se calculan los porcentaje de saturacion por maquina
        horas_usadas = [0, 0, 0, 0, 0, 0]
        una_semana = self.tiempo_actual + timedelta(days = 7)

        for evento in self.schedule:
            if self.tiempo_actual < evento.inicio < una_semana and type(evento) is not Falla:
                for i, m in enumerate(evento.recursos_necesitados):
                    if m:
                        horas_usadas[i] += DURACION_SESION[evento.paciente.patologia - 1]
            elif una_semana <= evento.inicio:
                break
        horas_semana = [54, 54, 54, 54, 54, 54]
        horas_totales = [a * b for a, b in zip(horas_semana, CANTIDAD_EQUIPO_PERSONAL_DISPONIBLE)]

        porcentajes_saturacion = [int(a/b*1000)/10 for a, b in zip(horas_usadas,horas_totales)]
        #print("S",porcentajes_saturacion)

        total_pacientes = sum(self.pacientes_atendiendose)
        porcentajes_pacientes = [int(a/total_pacientes*1000)/10 if total_pacientes!=0 else 0 for a in self.pacientes_atendiendose]
        #print("P",porcentajes_pacientes)

        """SE AGENDAN LAS SESIONES DE LOS NUEVOS PACIENTES
            LLEGADO EN EL LISTADO SEMANAL"""

        for paciente in pacientes:
            aceptado = True
            for r, s in zip(paciente.recursos_necesitados, porcentajes_saturacion):
                if r:
                    if 85 < s:
                        aceptado = False
                        self.pacientes_rechazados+= 1
                        break
                    elif 55 < s <= 85 and self.pacientes_atendiendose[paciente.patologia - 1] > self.alpha[paciente.patologia - 1]:
                        aceptado = False
                        self.pacientes_rechazados+= 1
                        break
                #if paciente.patologia == 3:
                #    aceptado = False

            if aceptado:
                self.pacientes_aceptados += 1
                self.pacientes_atendiendose[paciente.patologia - 1] += 1
                ##print(F'AGENDANDO PACIENTE {paciente.id}')
                paciente.ultima_sesion_cumplida = Evento(self.tiempo_actual,self.tiempo_actual)
                n_sesiones = paciente.cantidad_sesiones
                lista_sesiones = LinkedList(paciente, self.tiempo_actual, n_sesiones, self)
                for atencion in lista_sesiones:
                    self.agregar_evento(atencion)
                paciente.ultima_sesion_asignada = atencion

    #INPUT paciente: Paciente, hora_inicio: datetime, hora_max: datetime
    def asignar_sesion(self, paciente, hora_inicio, duracion):
        
        hora = hora_inicio
        sesion_asignada = False

        while (not sesion_asignada):
            
            if hora >= hora_inicio + 2*paciente.tiempo_max:
                sesion_asignada = True
                paciente.sesiones_asignadas += 1
                atencion = AtencionExterna(paciente, hora_inicio, hora_inicio + duracion)
                self.agregar_evento(atencion)
                paciente.ultima_sesion_asignada = atencion
                sesion_asignada = True
                break

            if self.disponible(paciente.recursos_necesitados, hora, hora + duracion):
                sesion_asignada = True
                paciente.sesiones_asignadas += 1
                atencion = Atencion(paciente, hora, hora + duracion)
                self.agregar_evento(atencion)
                paciente.ultima_sesion_asignada = atencion
            else:
                for evento in self.schedule:
                    if evento.final > hora:
                        hora = evento.final + timedelta(minutes = 5)
                        hora = self.check_horario_atencion(hora, duracion)
                        break

    #INPUT paciente: Paciente, inicio:datetime, final: datetime
    def disponible(self, recursos_necesitados, inicio, final):
        
        aux_recursos = self.recursos.copy()

        for evento in self.schedule:
            if evento.inicio < final and evento.final > inicio:
                for i, rec in enumerate(evento.recursos_necesitados):
                    aux_recursos[i] -= rec

            if evento.inicio > final:
                break

        for requerido, disponible in zip(recursos_necesitados, aux_recursos):
            if disponible < requerido:
                #print(disponible, requerido)
                return False

        return True

    #INPUT hora: datetime, duracion_sesion: timedelta
    def check_horario_atencion(self, hora, duracion_sesion):

        """VERIFICA QUE NO SE AGENDEN HORAS FUERA DE
        HORARIO DE ATENCION Y EN HORA DE COLACION"""

        #Ver que la hora de inicio y fin sea entre 8 y 18 hrs
        if time(0,0) < hora.time() < time(8,0) \
        or 0 <= (hora + duracion_sesion).hour < 8:
            hora = hora.replace(hour = 8, minute = 0)

        #si empieza o termina despues del cierre
        elif time(18,0) <= hora.time() < time(23,59)\
            or time(18,0) < (hora + duracion_sesion).time() < time(23,59):
            hora += timedelta(days = 1)
            hora = hora.replace(hour = 8, minute = 0)

        #si empieza o termina en hora de colacion (a las 13 hrs?)
        elif time(13,0) <= hora.time() < time(14,0) \
            or time(13,0) < (hora + duracion_sesion).time() <= time(14,0):
            hora = hora.replace(hour = 14, minute = 0)

        #OUTPUT hora: datetime
        return hora

    def check_conflicto(self, evento):

        conflicto = False
        for i, evento2 in enumerate(self.schedule):
            if evento2.inicio > evento.final:
                break
            if type(evento2) == Atencion and evento2.cumplido == False and evento2.id != evento.id:
                if evento2.inicio < evento.final and evento2.final > evento.inicio:
                    if not self.disponible([0,0,0,0,0,0], evento2.inicio, evento2.final):
                        self.reagendar_paciente(evento2.paciente, evento.final)
                        conflicto = True
                        ##print('conflicto', evento2.paciente.id, evento2.paciente.patologia)
                        break
        if conflicto:
            self.check_conflicto(evento)

    def reagendar_paciente(self, paciente, hora_inicio):

        aux = filter(lambda e: e.paciente.id != paciente.id if (type(e) in [Atencion, AtencionExterna]) else True, self.schedule)
        self.schedule = list(aux)
        paciente.ultima_sesion_asignada = None
        paciente.sesiones_asignadas = 0

        n_sesiones = paciente.cantidad_sesiones - len(paciente.sesiones_cumplidas)
        lista_sesiones = LinkedList(paciente, hora_inicio, n_sesiones, self)
        for atencion in lista_sesiones:
            self.agregar_evento(atencion)
        paciente.ultima_sesion_asignada = atencion


    def run(self):
        start_time = t()
        cambios = True
        ultimo_dia = self.tiempo_inicio - timedelta(days = 1)

        while self.schedule and cambios:

            for i, evento in enumerate(self.schedule):
                if evento.cumplido and self.tiempo_actual >= evento.final:
                    self.schedule.pop(i)
                    cambios = True
                    break

                elif (not evento.cumplido):
                    self.tiempo_actual = evento.inicio
                    if type(evento) is AsignacionSemanal:
                        self.asignacion_semanal(evento.lista_pacientes())
                        if self.tiempo_actual + timedelta(days = 7) < self.tiempo_fin:
                            nueva_asignacion = self.tiempo_actual + timedelta(days = 7)
                            self.agregar_evento(AsignacionSemanal(nueva_asignacion))

                    elif type(evento) is Atencion:
                        paciente = evento.paciente
                        paciente.sesiones_atendidas += 1
                        #falla = evento.falla()

                        if paciente.ausente() and False:
                            self.reagendar_paciente(paciente, evento.final)

                        elif False and falla and False:
                            '''if evento.inicio > paciente.ultima_sesion_cumplida.final + paciente.tiempo_max:
                                self.penalizaciones += paciente.penalidad
                                paciente.cantidad_sesiones += paciente.penalidad
                            self.agregar_evento(falla)
                            paciente.cantidad_sesiones += 1
                            self.asignar_sesion(paciente, paciente.ultima_sesion_asignada.final + paciente.tiempo_min, paciente.duracion_sesion)
                            paciente.sesiones_cumplidas.append(evento)
                            paciente.ultima_sesion_cumplida = evento'''
                            #self.reagendar_paciente(evento.paciente, evento.final)
                            #self.check_conflicto(falla)
                            n_sesiones = 0
                            if evento.inicio > paciente.ultima_sesion_cumplida.final_original + paciente.tiempo_max:
                                self.penalizaciones += paciente.penalidad
                                paciente.cantidad_sesiones += paciente.penalidad
                                #for i in range(paciente.penalidad):
                                #    self.asignar_sesion(paciente, paciente.ultima_sesion_asignada.final + paciente.tiempo_min, paciente.duracion_sesion)
                                n_sesiones += paciente.penalidad
                            lista_sesiones = LinkedList(paciente, paciente.ultima_sesion_cumplida.final+paciente.tiempo_min, n_sesiones + 1, self)
                            for atencion in lista_sesiones:
                                self.agregar_evento(atencion)
                            paciente.ultima_sesion_asignada = atencion
                            paciente.sesiones_cumplidas.append(evento)
                            paciente.ultima_sesion_cumplida = evento
                            paciente.cantidad_sesiones += 1
                            self.agregar_evento(falla)
                            self.check_conflicto(falla)
                            
                        else:
                            #evento.actualizar_duracion()
                            self.check_conflicto(evento)
                            if evento.inicio > paciente.ultima_sesion_cumplida.final_original + paciente.tiempo_max:
                                self.penalizaciones += paciente.penalidad
                                paciente.cantidad_sesiones += paciente.penalidad
                                #for i in range(paciente.penalidad):
                                #    self.asignar_sesion(paciente, paciente.ultima_sesion_asignada.final + paciente.tiempo_min, paciente.duracion_sesion)
                                n_sesiones = paciente.penalidad
                                lista_sesiones = LinkedList(paciente, paciente.ultima_sesion_cumplida.final+paciente.tiempo_min, n_sesiones, self)
                                for atencion in lista_sesiones:
                                    self.agregar_evento(atencion)
                                paciente.ultima_sesion_asignada = atencion



                            paciente.sesiones_cumplidas.append(evento)
                            paciente.ultima_sesion_cumplida = evento
                            if len(paciente.sesiones_cumplidas) == paciente.cantidad_sesiones:
                                self.pacientes_listos.append(paciente)
                                self.pacientes_atendiendose[paciente.patologia - 1] -= 1


                    elif type(evento) is AtencionExterna:
                        paciente = evento.paciente
                        if True:
                            paciente.sesiones_cumplidas.append(evento)
                            paciente.ultima_sesion_cumplida = evento
                            paciente.sesiones_cumplidas_externas += 1
                            if len(paciente.sesiones_cumplidas) == paciente.cantidad_sesiones:
                                self.pacientes_listos.append(paciente)
                                self.pacientes_atendiendose[paciente.patologia - 1] -= 1


                    evento.cumplido = True
                    cambios = True
                    break

                else:
                    cambios = False

                if ultimo_dia.date() < self.tiempo_actual.date():
                    dias = self.tiempo_actual - self.tiempo_inicio
                    self.dias.append(dias.days)
                    for i in range(9):
                        self.pacientes_diarios[i].append(self.pacientes_atendiendose[i])
                    self.pacientes_diarios[9].append(sum(self.pacientes_atendiendose))

                    ultimo_dia = self.tiempo_actual
        end_time = t()
        self.simulation_time = end_time - start_time



    def estadisticas(self):

        pacientes_por_patologia = [0,0,0,0,0,0,0,0,0]
        ingresos_por_patologia = [0,0,0,0,0,0,0,0,0]
        costos_interno = [0,0,0,0,0,0,0,0,0]
        costos_externo = [0,0,0,0,0,0,0,0,0]
        utilidad_por_patologia = [0,0,0,0,0,0,0,0,0]
        sesiones_externas = [0,0,0,0,0,0,0,0,0]
        sesiones_extra = [0,0,0,0,0,0,0,0,0]

        eventos1 = []

        for p in self.pacientes_listos:
            pat = p.patologia
            pacientes_por_patologia[pat - 1] += 1
            ingresos_por_patologia[pat - 1] += GANANCIA_POR_TRATAMIENTO[pat - 1]
            costos_interno[pat - 1] += COSTO_SESION_INTERNO[pat - 1] * p.sesiones_atendidas
            costos_externo[pat - 1] += COSTO_SESION_EXTERNO[pat - 1] * p.sesiones_cumplidas_externas
            sesiones_externas[pat - 1] += p.sesiones_cumplidas_externas
            sesiones_extra[pat - 1] += p.cantidad_sesiones - NRO_VISITAS[pat - 1]
            ##print(f'PACIENTE{p.id} PATOLOGIA{pat}')
            self.chequear_integridad(p)
            for evento in p.sesiones_cumplidas:
                eventos1.append(evento)
                ##print(evento.inicio, evento.final, evento.id, type(evento))

        #self.generar_calendario(eventos1, 0)
        #print('Pacientes atendidos',pacientes_por_patologia)
        #print('Ingresos',ingresos_por_patologia)
        #print('Costos interno',costos_interno)
        #print('Costos externo',costos_externo)
        #print()
        #print('Sesiones externas',sesiones_externas)
        #print('Sesiones extra',sesiones_extra)
        #print(self.externas)

        utilidad = sum(ingresos_por_patologia) - sum(costos_interno) - sum(costos_externo)
        #print('se demoro',self.simulation_time,'segundos')
        #print(utilidad)
        return utilidad

        #print(sum(sesiones_extra), self.penalizaciones)
        #print("Aceptados: ",self.pacientes_aceptados, "Rechazados: ",self.pacientes_rechazados)

        


        """for i in range(9):
            plt.plot(self.dias, self.pacientes_diarios[i], label = 'pat' + str(i+1))
        plt.plot(self.dias, self.pacientes_diarios[9], label = 'total')

        plt.xlabel('Tiempo')
        plt.ylabel('Pacientes')
        plt.title('Pacientes por patologia a en el tiempo')"""
        plt.show()

    def chequear_integridad(self, p):
        sesiones_teoricas = NRO_VISITAS[p.patologia - 1]
        sesiones_simulacion = len(p.sesiones_cumplidas)
        anterior = p.sesiones_cumplidas[0]
        i = 1
        ##print('tiempo maximo: ',p.tiempo_max)
        while i < sesiones_simulacion:
            actual = p.sesiones_cumplidas[i]
            if actual.inicio - anterior.final_original > p.tiempo_max:
                ##print(actual.inicio, actual.final_original)
                sesiones_teoricas += p.penalidad
            if actual.fallo:
                ##print('falla')
                sesiones_teoricas += 1

            i+=1
            anterior = actual

        ##print(sesiones_teoricas, sesiones_simulacion, sesiones_teoricas == sesiones_simulacion)
        #if sesiones_teoricas != sesiones_simulacion:
            #print('ERROR EN P ', p.patologia, sesiones_teoricas, sesiones_simulacion)


    def generar_calendario(self, eventos, maquina):

        rooms = ['M'+str(i+1) for i in range(self.recursos[maquina])]
        colors=['pink', 'lightgreen', 'lightblue', 'wheat', 'salmon', 'aqua', 'orchid', 'wheat', 'coral']

        days_labels = ['Day 1']

        eventos_dia = []
        
        eventos.sort(key=lambda evento: evento.inicio)
        n_days = (eventos[-1].inicio - eventos[0].inicio).days
        n_weeks = n_days//7 + 1
        lista_eventos = [[[] for j in range(n_days)]for i in range(n_weeks)]

        for evento in eventos:
            dias = (evento.inicio - eventos[0].inicio).days
            semana, dia = dias//7, dias%7
            if evento.recursos_necesitados[maquina]:
                lista_eventos[semana][dia].append(evento)
        
        fig, axs = plt.subplots(n_weeks, n_days)
        for w in range(n_weeks):
            for d in range(n_days):
                day_label = 'Day {0}'.format(w*7+d)
                agregados = []
                fig=plt.figure(figsize=(10,5.89))
                fig.clf()
                for e in lista_eventos[w][d]:
                    event = str(e.paciente.id) + 'Pat: ' + str(e.paciente.patologia)
                    maquina = 1
                    for e2 in agregados:
                        if e2.inicio < e.final and e2.final > e.inicio:
                            maquina += 1
                    agregados.append(e)
                    room=maquina-0.48
                    start=e.inicio.hour+e.inicio.minute/60
                    end=e.final.hour+e.final.minute/60
                    # plot event
                    plt.fill_between([room, room+0.96], [start, start], [end,end], color=colors[e.paciente.patologia-1], alpha=0.7, edgecolor='k', linewidth=0.5)
                    # plot beginning time
                    plt.text(room+0.02, start+0.05 ,'{0}:{1:0>2}'.format(e.inicio.hour,e.inicio.minute), va='top', fontsize=7)

                    # plot event name
                    plt.text(room+0.48, (start+end)*0.5, event, ha='center', va='center', fontsize=11)

                # Set Axis
                ax=fig.add_subplot(111)
                ax.yaxis.grid()
                ax.set_xlim(0.5,len(rooms)+0.5)
                ax.set_ylim(19.1, 7.9)
                ax.set_xticks(range(1,len(rooms)+1))
                ax.set_xticklabels(rooms)
                ax.set_ylabel('Time')

                # Set Second Axis
                ax2=ax.twiny().twinx()
                ax2.set_xlim(ax.get_xlim())
                ax2.set_ylim(ax.get_ylim())
                ax2.set_xticks(ax.get_xticks())
                ax2.set_xticklabels(rooms)
                ax2.set_ylabel('Time')
                


                plt.title(day_label,y=1.07)
                plt.savefig('{0}.png'.format(day_label), dpi=200)








