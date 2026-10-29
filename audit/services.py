from .models import AuditEvent
def record_event(actor,action,obj,summary,metadata=None):
 return AuditEvent.objects.create(actor=actor if getattr(actor,'is_authenticated',False) else None,action=action,object_type=obj.__class__.__name__,object_id=str(obj.pk),summary=summary,metadata=metadata or {})
