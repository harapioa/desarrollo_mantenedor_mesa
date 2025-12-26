from flask import Blueprint, render_template, flash, redirect, url_for
from .queries import get_detalle_at_asim

asim_bp = Blueprint('asim_bp', __name__)

@asim_bp.route('/detalle-at-asim/<int:acfi_id>')

def pagina_detalle_at_asim(acfi_id):
    # 1. Usamos la función maestra
    datos = get_detalle_at_asim(acfi_id)
    
    # 2. Validación de seguridad (La que fallaba antes)
    if not datos or not datos.get('info'):
        flash("No se encontró la Auditoría Simplificada solicitada.", "error")
        return redirect(url_for('pagina_principal'))
    
    # 3. Renderizamos
    return render_template(
        'ASIM/detalle_at_simplificada.html',  # Ruta en templates/ASIM/
        info=datos['info'],
        actividades=datos['actividades']
    )