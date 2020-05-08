from datetime import date, datetime, timedelta, time
from random import random
from entidades import Paciente, Evento, Atencion, AsignacionSemanal
from random import uniform, normalvariate, choice
from parametros import *


class CentroKine:

    #INPUT recursos: list int, tiempo_inicio: datetime, tiempo_fin: datetime
    def __init__(self, recursos, tiempo_inicio, tiempo_fin):

        self.schedule = []
        self.recursos = recursos
        self.tiempo_actual = tiempo_inicio
        self.tiempo_fin = tiempo_fin
        self.utilidad = 0
        self.pacientes_externo = 0
        self.pacientes_atentidos = 0
        self.cantidad_pacientes_con_problemas_por_equipo = [0, 0, 0, 0, 0, 0]

        primer_evento = AsignacionSemanal(self.tiempo_actual)
        self.agregar_evento(primer_evento)

    def agregar_evento(self, evento):

        """AGREGA UN NUEVO EVENTO AL SCHEDULE
           Y LA ORDENA SEGUN TIEMPO DE INICIO """

        self.schedule.append(evento)
        self.schedule.sort(key=lambda evento: evento.inicio)

    #INPUT pacientes: list Pacientes
    def asignacion_semanal(self, pacientes):

        """SE AGENDAN LAS SESIONES DE LOS NUEVOS PACIENTES
            LLEGADO EN EL LISTADO SEMANAL"""

        for paciente in pacientes:
            #print(F'AGENDANDO PACIENTE {paciente.id}, patologia {paciente.patologia}')
            for _ in range(paciente.cantidad_sesiones):
                if paciente.hora_ultima_sesion_asignada is None:
                    hora_inicio = self.tiempo_actual
                    hora_max = self.tiempo_actual + paciente.tiempo_max
                else:
                    hora_inicio = paciente.hora_ultima_sesion_asignada + paciente.tiempo_min
                    hora_max = paciente.hora_ultima_sesion_asignada + paciente.tiempo_min + paciente.tiempo_max
                self.asignar_sesion(paciente, hora_inicio, hora_max)

    def asignacion_falla(self, eventos, )

    #INPUT paciente: Paciente, hora_inicio: datetime, hora_max: datetime
    def asignar_sesion(self, paciente, hora_inicio, hora_max):
        
        hora = hora_inicio
        sesion_asignada = False

        while (not sesion_asignada):

            if hora > hora_max:
                #print("No se recibe al paciente")
                break

            if self.verificar_disponibilidad(paciente, hora, hora + paciente.duracion_sesion, self.recursos):
                sesion_asignada = True
                paciente.sesiones_asignadas += 1
                paciente.hora_ultima_sesion_asignada = hora

                atencion = Atencion(paciente, hora, hora + paciente.duracion_sesion)
                self.agregar_evento(atencion)
                
                #print(f'Sesion {paciente.sesiones_asignadas}')
                #print(f'Inicio: {hora}, Fin: {hora + paciente.duracion_sesion}')
                break
            else:
                for evento in self.schedule:
                    if evento.final > hora:
                        hora = evento.final
                        hora = self.check_horario_atencion(hora, paciente.duracion_sesion)
                        break

    #INPUT paciente: Paciente, inicio:datetime, final: datetime
    def verificar_disponibilidad(self, paciente, inicio, final, recursos):
        
        aux_recursos = recusos

        for evento in self.schedule:
            if evento.inicio < final and evento.final > inicio:
                for i, rec in enumerate(evento.recursos_necesitados):
                    aux_recursos[i] -= rec

            if evento.inicio > final:
                break

        for requerido, disponible in zip(paciente.recursos_necesitados, aux_recursos):
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

    def run(self):
        
        while self.tiempo_actual < self.tiempo_fin:

            

            for i, evento in enumerate(self.schedule):
                if evento.cumplido and self.tiempo_actual > evento.final:
                    self.schedule.pop(i)
                    break #hay que termiar el ciclo porque se altero la lista sobre la que se esta iterando

                elif (not evento.cumplido):
                    self.tiempo_actual = evento.inicio

                    if type(evento) == AsignacionSemanal:
                        self.asignacion_semanal(evento.lista_pacientes())
                        nueva_asignacion = self.tiempo_actual + timedelta(days = 7)
                        self.agregar_evento(AsignacionSemanal(nueva_asignacion))

                    elif type(evento) == Atencion:
                        eventos_afectados_falla_equipo = []
                        eventos_afectados_ausente = []
                        tiempo_ausentismo = 0
                        tiempo_falla = 0

                        for equipo, cantidad in enumerate(evento.paciente.recursos_necesitados[:5]):
                            if cantidad != 0 and random() <= PROBA_FALLA_EQUIPO:
                                tiempo_falla = uniform(evento.inicio, evento.final)
                                print(f'falló {EQUIPO[equipo]} a las {tiempo_falla}')
                                eventos_afectados_falla_equipo = list(filter(lambda event: tiempo_falla <= event.inicio
                                                                        <= tiempo_falla +
                                                                        timedelta(hours=
                                                                                  DURACION_FALLA) and type(event) == Atencion
                                                                        and event.paciente.recursos_necesitados[equipo]!=0, self.schedule))
                                self.cantidad_pacientes_con_problemas_por_equipo[equipo] += len(eventos_afectados_falla_equipo) 

                        if evento.paciente.recursos_necesitados[5] != 0 and random() <= PROBA_AUSENTISMO:
                            tiempo_ausentismo = uniform(evento.inicio, evento.final)
                            print(f'falló {EQUIPO[5]} a las {tiempo_ausentismo}')
                            eventos_afectados_ausente = list(filter(lambda event: tiempo_ausentismo <= event.inicio
                                                                    <= tiempo_ausentismo +
                                                                    timedelta(hours=DURACION_FALLA)
                                                                    and type(event) == Atencion,
                                                                    self.schedule))
                            self.cantidad_pacientes_con_problemas_por_equipo[5] += len(eventos_afectados_ausente)
                        eventos_afectados = eventos_afectados_ausente + list(set(eventos_afectados_falla_equipo) - set(eventos_afectados_ausente))

                        print(self.cantidad_pacientes_con_problemas_por_equipo)
                        if len(eventos_afectados) > 0:
                            print(eventos_afectados)
                        #print(f'Atendiendo persona, {evento.paciente.id}')
                        #print('Inicio', evento.inicio)
                        #print('Final', evento.final)
                    evento.cumplido = True
                    break













