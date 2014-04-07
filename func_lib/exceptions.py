def just_try(function, args):
  try:
    function(*args)
  except:
    pass
