// Funciones AJAX para tableros - app/static/js/tableros.js

// ===== AGREGAR NUEVA LISTA =====
function agregarLista(tableroId) {
    const nombre = prompt('Nombre de la nueva lista:');
    
    if (!nombre || nombre.trim() === '') {
        return;
    }
    
    const color = prompt('Color (opcional, presiona Enter para usar azul):') || '#3b82f6';
    
    fetch('/tableros/agregar_lista', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tablero_id: tableroId,
            nombre: nombre.trim(),
            color: color
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar página para mostrar nueva lista
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'No se pudo crear la lista'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// ===== AGREGAR NUEVA TARJETA =====
function agregarTarjeta(listaId) {
    const titulo = prompt('Título de la nueva tarjeta:');
    
    if (!titulo || titulo.trim() === '') {
        return;
    }
    
    const descripcion = prompt('Descripción (opcional):') || '';
    const responsable = prompt('Responsable (opcional):') || '';
    
    fetch('/tableros/agregar_tarjeta', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            lista_id: listaId,
            titulo: titulo.trim(),
            descripcion: descripcion.trim(),
            responsable: responsable.trim()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar página para mostrar nueva tarjeta
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'No se pudo crear la tarjeta'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// ===== ELIMINAR LISTA =====
function eliminarLista(listaId, nombreLista) {
    if (!confirm(`¿Estás seguro de que quieres eliminar la lista "${nombreLista}"?\n\nSolo se pueden eliminar listas vacías.`)) {
        return;
    }
    
    fetch(`/tableros/eliminar_lista/${listaId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar página para reflejar cambios
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'No se pudo eliminar la lista'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// ===== ELIMINAR TARJETA =====
function eliminarTarjeta(tarjetaId, tituloTarjeta) {
    if (!confirm(`¿Estás seguro de que quieres eliminar la tarjeta "${tituloTarjeta}"?`)) {
        return;
    }
    
    fetch(`/tableros/eliminar_tarjeta/${tarjetaId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar página para reflejar cambios
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'No se pudo eliminar la tarjeta'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// ===== FUNCIONES AUXILIARES =====
function mostrarMensaje(mensaje, tipo = 'info') {
    // Función simple para mostrar mensajes
    const alertClass = tipo === 'error' ? 'alert-danger' : 
                      tipo === 'success' ? 'alert-success' : 'alert-info';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de tableros cargado correctamente');
    
    // Aquí puedes añadir inicializaciones adicionales
    // como drag & drop, actualización automática, etc.
});