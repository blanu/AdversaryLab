function login(model)
{
  user.isLoggedIn(function(result) {
    log('isLogginedIn '+result);
    if(result)
    {
      user.logout(function(uri) {
        model.logout(uri);
      });
      
      user.isAdmin(function(result) {
        log('isAdmin: '+result);
        model.admin(result);        
      });      
    }
    else
    {
      window.location='/welcome';
    }
  });
}