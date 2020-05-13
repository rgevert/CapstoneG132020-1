from datetime import date, datetime, timedelta, time

from entidades import Paciente, Evento, Atencion, AtencionExterna, AsignacionSemanal
from random import uniform, normalvariate, choice, seed as rseed
from parametros import *

#rseed(0)

class CentroKine:

    #INPUT recursos: list int, tiempo_inicio: datetime, tiempo_fin: datetime
    def __init__(self, tiempo_inicio, tiempo_fin):
        self.penalizaciones = 0
        self.schedule = []
        self.recursos = CANTIDAD_EQUIPO_PERSONAL_DISPONIBLE
        self.tiempo_actual = tiempo_inicio
        self.tiempo_fin = tiempo_fin
        self.externas = 0

        primer_evento = AsignacionSemanal(self.tiempo_actual)
        self.agregar_evento(primer_evento)

        #ATRIBUTOS PARA ESTADISTICAS
        self.pacientes_listos = []

    def agregar_evento(self, evento):

        """AGREGA UN NUEVO EVENTO AL SCHEDULE
           Y LA ORDENA SEGUN TIEMPO DE INICIO """

        self.schedule.append(evento)
        self.schedule.sort(key=lambda evento: evento.inicio)

    def asignacion_semanal(self, pacientes):

        """SE AGENDAN LAS SESIONES DE LOS NUEVOS PACIENTES
            LLEGADO EN EL LISTADO SEMANAL"""

        for paciente in pacientes:
            #print(F'AGENDANDO PACIENTE {paciente.id}')
            paciente.ultima_sesion_cumplida = Evento(self.tiempo_actual,self.tiempo_actual)
            paciente.ultima_sesion_asignada = Evento(self.tiempo_actual,self.tiempo_actual)
            while paciente.sesiones_asignadas < paciente.cantidad_sesiones:
                if paciente.ultima_sesion_asignada is None:
                    hora_inicio = self.tiempo_actual
                else:
                    hora_inicio = paciente.ultima_sesion_asignada.final + paciente.tiempo_min
                hora_inicio = self.check_horario_atencion(hora_inicio, paciente.duracion_sesion)
                self.asignar_sesion(paciente, hora_inicio, paciente.duracion_sesion)

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
                        hora = evento.final + timedelta(minutes = 3)
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

        for i, evento2 in enumerate(self.schedule):
            if evento2.inicio > evento.final:
                break
            if type(evento2) == Atencion and evento2.cumplido == False and evento2.id != evento.id:
                if not self.disponible([0,0,0,0,0,0], evento2.inicio, evento2.final):
                    self.reagendar_paciente(evento2.paciente, evento.final)
                    self.check_conflicto(evento)
                    break

    def reagendar_paciente(self, paciente, hora_inicio):

        aux = filter(lambda e: e.paciente.id != paciente.id if (type(e) in [Atencion, AtencionExterna]) else True, self.schedule)
        self.schedule = list(aux)
        paciente.ultima_sesion_asignada = None
        paciente.sesiones_asignadas = 0

        for _ in range(paciente.cantidad_sesiones - len(paciente.sesiones_cumplidas)):
                if paciente.ultima_sesion_asignada is not None:
                    hora_inicio = paciente.ultima_sesion_asignada.final + paciente.tiempo_min
                hora_inicio = self.check_horario_atencion(hora_inicio, paciente.duracion_sesion)
                self.asignar_sesion(paciente, hora_inicio, paciente.duracion_sesion)


    def run(self):
        cambios = True
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
                        falla = evento.falla()

                        if paciente.ausente():
                            self.reagendar_paciente(paciente, evento.final)

                        elif falla and False:
                            if evento.inicio > paciente.ultima_sesion_cumplida.final + paciente.tiempo_max:
                                self.penalizaciones += paciente.penalidad
                                paciente.cantidad_sesiones += paciente.penalidad
                            self.agregar_evento(falla)
                            paciente.cantidad_sesiones += 1
                            self.asignar_sesion(paciente, paciente.ultima_sesion_asignada.final + paciente.tiempo_min, paciente.duracion_sesion)
                            paciente.sesiones_cumplidas.append(evento)
                            paciente.ultima_sesion_cumplida = evento
                            #self.reagendar_paciente(evento.paciente, evento.final)
                            #self.check_conflicto(falla)
                            
                        else:
                            evento.actualizar_duracion()
                            self.check_conflicto(evento)
                            if evento.inicio > paciente.ultima_sesion_cumplida.final + paciente.tiempo_max:
                                self.penalizaciones += paciente.penalidad
                                paciente.cantidad_sesiones += paciente.penalidad
                                for i in range(paciente.penalidad):
                                    self.asignar_sesion(paciente, paciente.ultima_sesion_asignada.final + paciente.tiempo_min, paciente.duracion_sesion)
                            paciente.sesiones_cumplidas.append(evento)
                            paciente.ultima_sesion_cumplida = evento
                            if len(paciente.sesiones_cumplidas) == paciente.cantidad_sesiones:
                                self.pacientes_listos.append(paciente)


                    elif type(evento) is AtencionExterna:
                        paciente = evento.paciente
                        if True:
                            paciente.sesiones_cumplidas.append(evento)
                            paciente.ultima_sesion_cumplida = evento
                            paciente.sesiones_cumplidas_externas += 1
                            if len(paciente.sesiones_cumplidas) == paciente.cantidad_sesiones:
                                self.pacientes_listos.append(paciente)


                    evento.cumplido = True
                    cambios = True
                    break

                else:
                    cambios = False

    def estadisticas(self):

        pacientes_por_patologia = [0,0,0,0,0,0,0,0,0]
        ingresos_por_patologia = [0,0,0,0,0,0,0,0,0]
        costos_interno = [0,0,0,0,0,0,0,0,0]
        costos_externo = [0,0,0,0,0,0,0,0,0]
        utilidad_por_patologia = [0,0,0,0,0,0,0,0,0]
        sesiones_externas = [0,0,0,0,0,0,0,0,0]
        sesiones_extra = [0,0,0,0,0,0,0,0,0]

        for p in self.pacientes_listos:
            pat = p.patologia
            pacientes_por_patologia[pat - 1] += 1
            ingresos_por_patologia[pat - 1] += GANANCIA_POR_TRATAMIENTO[pat - 1]
            costos_interno[pat - 1] += COSTO_SESION_INTERNO[pat - 1] * p.sesiones_atendidas
            costos_externo[pat - 1] += COSTO_SESION_EXTERNO[pat - 1] * p.sesiones_cumplidas_externas
            sesiones_externas[pat - 1] += p.sesiones_cumplidas_externas
            sesiones_extra[pat - 1] += p.cantidad_sesiones - NRO_VISITAS[pat - 1]
            print(f'PACIENTE{p.id} PATOLOGIA{pat}')
            for evento in p.sesiones_cumplidas:
                print(evento.inicio, evento.final, evento.id, type(evento))

        print('Pacientes atendidos',pacientes_por_patologia)
        print('Ingresos',ingresos_por_patologia)
        print('Costos interno',costos_interno)
        print('Costos externo',costos_externo)
        print()
        print('Sesiones externas',sesiones_externas)
        print('Sesiones extra',sesiones_extra)
        print(self.externas)

        utilidad = sum(ingresos_por_patologia) - sum(costos_interno) - sum(costos_externo)
        print(utilidad)

        print(sum(sesiones_extra), self.penalizaciones)