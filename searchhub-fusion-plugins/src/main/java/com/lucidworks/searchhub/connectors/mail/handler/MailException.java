package com.lucidworks.searchhub.connectors.mail.handler;

public class MailException extends Exception {

  /**
   *
   */
  private static final long serialVersionUID = -1056713749813910936L;

  public MailException(String string, Throwable e) {
    super(string, e);
  }

}
