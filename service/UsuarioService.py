from repository.UsuarioRepository import UsuarioRepository
from repository.PerfilUsuarioRepository import PerfilUsuarioRepository
from typing import Optional, Dict, List
from datetime import date


class UsuarioService:
    """Servicio para operaciones de negocio de Usuario y su Perfil"""

    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.perfil_repo = PerfilUsuarioRepository()

    def crear_usuario_completo(self, usuario_data: dict, perfil_data: dict = None) -> Optional[Dict]:
        """Crear usuario con perfil opcional"""
        try:
            # Crear usuario
            usuario = self.usuario_repo.crear_usuario(usuario_data)
            if not usuario:
                return None

            resultado = {
                'usuario': usuario,
                'perfil': None,
                'mensaje': 'Usuario creado exitosamente'
            }

            # Crear perfil si se proporciona
            if perfil_data:
                perfil_data['id_usuario'] = usuario.id_usuario
                perfil = self.perfil_repo.crear_perfil(perfil_data)
                resultado['perfil'] = perfil
                if perfil:
                    resultado['mensaje'] = 'Usuario y perfil creados exitosamente'

            return resultado

        except Exception as e:
            print(f"Error creando usuario completo: {e}")
            return None

    def obtener_usuario_completo(self, id_usuario: int) -> Optional[Dict]:
        """Obtener usuario con su perfil"""
        try:
            usuario = self.usuario_repo.obtener_usuario_por_id(id_usuario)
            if not usuario:
                return None

            perfil = self.perfil_repo.obtener_perfil_por_usuario(id_usuario)

            return {
                'usuario': usuario,
                'perfil': perfil,
                'tiene_perfil': perfil is not None
            }

        except Exception as e:
            print(f"Error obteniendo usuario completo: {e}")
            return None

    def actualizar_usuario_completo(self, id_usuario: int, usuario_data: dict = None,
                                    perfil_data: dict = None) -> Optional[Dict]:
        """Actualizar usuario y/o perfil"""
        try:
            resultado = {'usuario': None, 'perfil': None, 'mensaje': ''}

            # Actualizar usuario si se proporciona data
            if usuario_data:
                usuario = self.usuario_repo.actualizar_usuario(id_usuario, usuario_data)
                resultado['usuario'] = usuario
                if usuario:
                    resultado['mensaje'] += 'Usuario actualizado. '

            # Actualizar perfil si se proporciona data
            if perfil_data:
                perfil = self.perfil_repo.actualizar_perfil(id_usuario, perfil_data)
                resultado['perfil'] = perfil
                if perfil:
                    resultado['mensaje'] += 'Perfil actualizado. '
                elif not self.perfil_repo.perfil_existe(id_usuario):
                    # Crear perfil si no existe
                    perfil_data['id_usuario'] = id_usuario
                    perfil = self.perfil_repo.crear_perfil(perfil_data)
                    resultado['perfil'] = perfil
                    if perfil:
                        resultado['mensaje'] += 'Perfil creado. '

            return resultado if resultado['mensaje'] else None

        except Exception as e:
            print(f"Error actualizando usuario completo: {e}")
            return None

    def eliminar_usuario_completo(self, id_usuario: int) -> bool:
        """Eliminar usuario y su perfil"""
        try:
            # Eliminar perfil primero (si existe)
            if self.perfil_repo.perfil_existe(id_usuario):
                self.perfil_repo.eliminar_perfil(id_usuario)

            # Eliminar usuario
            return self.usuario_repo.eliminar_usuario(id_usuario)

        except Exception as e:
            print(f"Error eliminando usuario completo: {e}")
            return False

    def validar_credenciales(self, email: str, password: str) -> Optional[Dict]:
        """Validar credenciales y obtener usuario completo"""
        try:
            usuario = self.usuario_repo.obtener_usuario_por_email(email)
            if not usuario:
                return None

            # Aquí deberías verificar la contraseña (hash)
            # Por simplicidad, comparación directa
            if usuario.password == password:
                perfil = self.perfil_repo.obtener_perfil_por_usuario(usuario.id_usuario)
                return {
                    'usuario': usuario,
                    'perfil': perfil,
                    'autenticado': True
                }

            return None

        except Exception as e:
            print(f"Error validando credenciales: {e}")
            return None

    def buscar_usuarios_por_criterios(self, criterios: dict) -> List[Dict]:
        """Buscar usuarios con filtros múltiples"""
        try:
            usuarios = []

            # Buscar por email si se proporciona
            if 'email' in criterios:
                usuario = self.usuario_repo.obtener_usuario_por_email(criterios['email'])
                if usuario:
                    usuarios = [usuario]

            # Buscar por nombre si se proporciona
            elif 'nombre' in criterios:
                usuarios = self.usuario_repo.buscar_usuarios_por_nombre(criterios['nombre'])

            # Si hay criterios de perfil, filtrar usuarios
            else:
                usuarios = self.usuario_repo.obtener_todos_usuarios()

            # Agregar información de perfil y filtrar por criterios de perfil
            resultado = []
            for usuario in usuarios:
                perfil = self.perfil_repo.obtener_perfil_por_usuario(usuario.id_usuario)

                # Aplicar filtros de perfil
                incluir = True
                if 'edad_min' in criterios and perfil and perfil.edad:
                    if perfil.edad < criterios['edad_min']:
                        incluir = False

                if 'edad_max' in criterios and perfil and perfil.edad:
                    if perfil.edad > criterios['edad_max']:
                        incluir = False

                if 'ocupacion' in criterios and perfil and perfil.ocupacion:
                    if criterios['ocupacion'].lower() not in perfil.ocupacion.lower():
                        incluir = False

                if incluir:
                    resultado.append({
                        'usuario': usuario,
                        'perfil': perfil
                    })

            return resultado

        except Exception as e:
            print(f"Error buscando usuarios: {e}")
            return []

    def obtener_estadisticas_usuarios(self) -> Dict:
        """Obtener estadísticas generales de usuarios y perfiles"""
        try:
            total_usuarios = len(self.usuario_repo.obtener_todos_usuarios())
            total_perfiles = len(self.perfil_repo.obtener_todos_perfiles())

            estadisticas_edad = self.perfil_repo.obtener_estadisticas_edad()

            return {
                'total_usuarios': total_usuarios,
                'total_perfiles': total_perfiles,
                'usuarios_con_perfil': total_perfiles,
                'usuarios_sin_perfil': total_usuarios - total_perfiles,
                'porcentaje_con_perfil': round((total_perfiles / total_usuarios * 100), 2) if total_usuarios > 0 else 0,
                'estadisticas_edad': estadisticas_edad
            }

        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {}

    def calcular_imc_usuario(self, id_usuario: int) -> Optional[Dict]:
        """Calcular IMC y clasificación del usuario"""
        try:
            imc = self.perfil_repo.calcular_imc_usuario(id_usuario)
            if imc is None:
                return None

            # Clasificación de IMC
            if imc < 18.5:
                clasificacion = "Bajo peso"
            elif 18.5 <= imc < 24.9:
                clasificacion = "Peso normal"
            elif 25 <= imc < 29.9:
                clasificacion = "Sobrepeso"
            else:
                clasificacion = "Obesidad"

            return {
                'imc': imc,
                'clasificacion': clasificacion,
                'id_usuario': id_usuario
            }

        except Exception as e:
            print(f"Error calculando IMC: {e}")
            return None

    def usuarios_activos_por_fecha(self, fecha_desde: date) -> List[Dict]:
        """Obtener usuarios registrados desde una fecha específica"""
        try:
            usuarios = self.usuario_repo.obtener_usuarios_por_fecha(fecha_desde)
            resultado = []

            for usuario in usuarios:
                perfil = self.perfil_repo.obtener_perfil_por_usuario(usuario.id_usuario)
                resultado.append({
                    'usuario': usuario,
                    'perfil': perfil
                })

            return resultado

        except Exception as e:
            print(f"Error obteniendo usuarios por fecha: {e}")
            return []