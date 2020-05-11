from datetime import date, datetime, timedelta, time

from entidades import Paciente, Evento, Atencion, AtencionExterna, AsignacionSemanal
from random import uniform, normalvariate, choice
from parametros import *


class CentroKine:

    #INPUT recursos: list int, tiempo_inicio: datetime, tiempo_fin: datetime
    def __init__(self, tiempo_inicio, tiempo_fin):

        self.schedule = []
        self.recursos = CANTIDAD_EQUIPO_PERSONAL_DISPONIBLE
        self.tiempo_actual = tiempo_inicio
        self.tiempo_fin = tiempo_fin

        primer_evento = AsignacionSemanal(self.tiempo_actual)
        self.agregar_evento(primer_evento)

        #ATRIBUTOS PARA ESTADISTICAS
        self.pacientes_listos = []
        self.recurso_limitante = [0,0,0,0,0,0]

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
            #print(F'AGENDANDO PACIENTE {paciente.id}')
            for _ in range(paciente.cantidad_sesiones):
                if paciente.hora_ultima_sesion_asignada is None:
                    hora_inicio = self.tiempo_actual
                else:
                    hora_inicio = paciente.hora_ultima_sesion_asignada + paciente.tiempo_min
                self.asignar_sesion(paciente, hora_inicio)

    #INPUT paciente: Paciente, hora_inicio: datetime, hora_max: datetime
    def asignar_sesion(self, paciente, hora_inicio):
        
        hora = hora_inicio
        sesion_asignada = False
        penalizado = False

        while (not sesion_asignada):

            if hora > hora_inicio + paciente.tiempo_max and not penalizado:
                paciente.cantidad_sesiones += paciente.penalidad
                penalizado = True
                break

            if hora > hora_inicio + 2*paciente.tiempo_max:
                paciente.sesiones_asignadas += 1
                atencion = AtencionExterna(paciente, hora_inicio, hora_inicio + paciente.duracion_sesion)

            elif self.verificar_disponibilidad(paciente, hora, hora + paciente.duracion_sesion):
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
    def verificar_disponibilidad(self, paciente, inicio, final):
        
        aux_recursos = self.recursos.copy()

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

    def reagendar_paciente(self, paciente, hora_inicio):

        aux = filter(lambda e: e.paciente.id != paciente.id if type(e) == Atencion else True, self.schedule)
        self.schedule = list(aux)

        paciente.hora_ultima_sesion_asignada = None
        paciente.sesiones_asignadas = 0

        for _ in range(paciente.cantidad_sesiones - paciente.sesiones_cumplidas):
                if paciente.hora_ultima_sesion_asignada is not None:
                    hora_inicio = paciente.hora_ultima_sesion_asignada + paciente.tiempo_min
                self.asignar_sesion(paciente, hora_inicio)



    def check_conflicto(self, hora_inicio, hora_final, paciente = None):

        for i, evento in enumerate(self.schedule):
            if evento.inicio > hora_final:
                break
            if type(evento) == Atencion:
                if not self.sigue_disponible(evento.paciente, evento.inicio, evento.final):
                    self.reagendar_paciente(evento.paciente, hora_inicio)
                    self.check_conflicto(hora_inicio, hora_final, paciente)
                    break

    def sigue_disponible(self, paciente, inicio, final):
        
        aux_recursos = self.recursos.copy()

        for evento in self.schedule:
            if evento.inicio < final and evento.final > inicio:
                for i, rec in enumerate(evento.recursos_necesitados):
                    aux_recursos[i] -= rec

            if evento.inicio > final:
                break

        for i, disponible in enumerate(aux_recursos):
            if disponible < 0:
                if paciente.recursos_necesitados[i]:
                    return False
        return True

    def run(self):
        
        while self.tiempo_actual < self.tiempo_fin and self.schedule:
            #print(self.schedule)

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
                        falla = evento.falla()
                        evento.actualizar_duracion()
                        evento.paciente.sesiones_atendidas += 1
                        if evento.ausente():
                            #print("AUSENTE")
                            hora_inicio = self.tiempo_actual + timedelta(hours = 1)
                            self.reagendar_paciente(evento.paciente, self.tiempo_actual)
                        
                        elif falla:
                            #print('FALLA')
                            self.agregar_evento(falla)
                            self.reagendar_paciente(evento.paciente, self.tiempo_actual)
                            self.check_conflicto(falla.inicio, falla.final)
                        else:
                            evento.paciente.sesiones_cumplidas += 1
                            self.check_conflicto(evento.inicio, evento.final)
                            if evento.paciente.sesiones_cumplidas == evento.paciente.cantidad_sesiones:
                                self.pacientes_listos.append(evento.paciente)

                    elif type(evento) == AtencionExterna:
                        evento.paciente.sesiones_cumplidas += 1
                        evento.paciente.sesiones_cumplidas_externas += 1


                    evento.cumplido = True
                    break

    def estadisticas(self):

        pacientes_por_patologia = [0,0,0,0,0,0,0,0,0]
        ingresos_por_patologia = [0,0,0,0,0,0,0,0,0]
        costos_por_patologia = [0,0,0,0,0,0,0,0,0]
        utilidad_por_patologia = [0,0,0,0,0,0,0,0,0]

        for p in self.pacientes_listos:
            pat = p.patologia
            pacientes_por_patologia[pat - 1] += 1
            ingresos_por_patologia[pat - 1] += GANANCIA_POR_TRATAMIENTO[pat - 1]
            costos_por_patologia[pat - 1] += COSTO_SESION_INTERNO[pat - 1] * p.sesiones_atendidas
            costos_por_patologia[pat - 1] += COSTO_SESION_EXTERNO[pat - 1] * p.sesiones_cumplidas_externas

        print(pacientes_por_patologia)
        print(ingresos_por_patologia)
        print(costos_por_patologia)

        utilidad = sum(ingresos_por_patologia) - sum(costos_por_patologia)
        print(utilidad)






