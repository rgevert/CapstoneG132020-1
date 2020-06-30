from entidades import Evento, Atencion, AtencionExterna
from datetime import date, datetime, timedelta, time

class Node:
	def __init__(self,paciente, i):
		self.i = i
		self.paciente = paciente
		self.atencion = None
		self.next = None
		self.prev = None
		


	def asignar(self, hora_inicio):

		duracion = self.paciente.duracion_sesion
		hora_inicio = self.kine.check_horario_atencion(hora_inicio, duracion)
		hora = hora_inicio
		sesion_asignada = False

		while (not sesion_asignada):

			if hora >= self.prev.atencion.final + duracion + self.paciente.tiempo_max and self.kine.disponible(self.paciente.recursos_necesitados, hora, hora + duracion):
				
				atencion = Atencion(self.paciente, hora, hora + duracion, self.paciente.patologia)
				#print('intenando agendar ', self.i, ' en ', hora)
				if self.prev and self.prev.ajustar(atencion):
					self.atencion = atencion
				else:
					self.atencion = AtencionExterna(self.paciente, hora_inicio, hora_inicio + duracion)
				sesion_asignada = True
				break

			if self.kine.disponible(self.paciente.recursos_necesitados, hora, hora + duracion):
				sesion_asignada = True
				#print(self.i)
				self.atencion = Atencion(self.paciente, hora, hora + duracion, self.paciente.patologia)
			else:
				for evento in self.kine.schedule:
					if evento.final > hora:
						hora = evento.final + timedelta(minutes = 5)
						hora = self.kine.check_horario_atencion(hora, duracion)
						break

		if self.i < self.n:
			new_node = Node(self.paciente, self.i + 1)
			self.next = new_node
			new_node.prev = self
			new_node.asignar(self.atencion.final + self.paciente.tiempo_min)

	def ajustar(self, atencion):
		#print('ajustando nodo ',self.i, ' hora con inicio', atencion.inicio)
		duracion = self.paciente.duracion_sesion
		#print('holaaaa ',atencion.inicio - self.paciente.tiempo_max)
		hora_inicio = self.kine.check_horario_atencion(atencion.inicio - self.paciente.tiempo_max, duracion)
		hora = hora_inicio

		#print('hora despues de check ',hora)

		if self.i == -1:
			return False

		while True:
			if hora >= atencion.inicio - self.paciente.tiempo_min:
				#print('chau',hora,atencion.inicio - self.paciente.tiempo_min)
				return False

			elif type(self.atencion) is AtencionExterna or self.kine.disponible(self.paciente.recursos_necesitados, hora, hora + duracion):

				if type(self.atencion) is AtencionExterna:
					tentativa = AtencionExterna(self.paciente, hora, hora + duracion)
				else:
					tentativa = Atencion(self.paciente, hora, hora + duracion, self.paciente.patologia)
					#print('tentativa',tentativa.inicio)
				if tentativa.inicio <= self.prev.atencion.final + self.paciente.tiempo_max:
					#print('perfecto')
					self.atencion = tentativa
					return True
				elif self.prev and self.prev.ajustar(tentativa):
					self.atencion = tentativa
					return True
				else:
					return False

			else:
				for evento in self.kine.schedule:
					if evento.final > hora:
						hora = evento.final + timedelta(minutes = 5)
						hora = self.kine.check_horario_atencion(hora, duracion)
						break



class LinkedList:
	def __init__(self, paciente, inicio, n, kine):
		Node.kine = kine
		Node.n = n
		dummynode = Node(paciente, -1)
		dummynode.atencion = Evento(inicio, inicio)
		self.head = Node(paciente, 1)
		self.head.prev = dummynode
		self.head.asignar(inicio)

	def __iter__(self):
		return LinkedListIterator(self.head)

class LinkedListIterator:
	def __init__(self, head):
		self.current = head

	def __iter__(self):
		return self

	def __next__(self):
		if not self.current:
			raise StopIteration
		else:
			item = self.current.atencion
			self.current = self.current.next
			return item

