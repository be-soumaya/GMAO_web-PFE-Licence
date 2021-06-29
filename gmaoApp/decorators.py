from django.http import HttpResponse
from django.shortcuts import redirect


def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		def wrapper_func(request, *args, **kwargs):

			group = None
			if request.user.groups.exists():
				group = request.user.groups.all()[0].name

			if group in allowed_roles:
				return view_func(request, *args, **kwargs)
			else:
				return HttpResponse('<head><link href="//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css" rel="stylesheet"><link href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" rel="stylesheet"><style> .container {margin-top: 50px;} .alert-danger {border-color: #e6e6e6;border-left: 5px solid #c82630;background-color: #fff;color: #888;}@media (min-width: 768px) { .alert {border-radius: 6px;display: table;width: 100%;padding-left: 78px;position: relative;padding-right: 60px;border: 1px solid #e6e6e6;}  .alert .icon {text-align: center;width: 58px;height: 100%;position: absolute;top: 0;left: 0;border: 1px solid #bdbdbd;padding-top: 15px;border-radius: 6px 0 0 6px;} .alert .icon i {font-size: 20px;color: #fff;left: 21px;margin-top: -10px;position: absolute;top: 50%;} .alert .icon img {font-size: 20px;color: #fff;left: 18px;margin-top: -10px;position: absolute;top: 50%;}   .alert.alert-danger .icon, .alert.alert-danger .icon:after {border-color: none;background: #c82630;} }</style></head><div class="container"><div class="alert alert-danger"><div class="icon hidden-xs"><i class="fa fa-lock"></i></div><strong>Accès interdit</strong><Br />  Désolé, vous n\'êtes pas autorisé à accéder à cette page.</div></div>')
		return wrapper_func
	return decorator
