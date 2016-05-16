package com.lucidworks.searchhub.connectors.mail.handler;


import com.lucidworks.searchhub.connectors.util.Hash;

public class SimpleMailHash implements MailHash {

  @Override
  public String calculateHash(String data) {

    return Long.toHexString(Hash.lookup3ycs64(data, 0, data.length(), 0));
  }

}
