package com.lucidworks.searchhub.connectors.util;


/**
 * Various hash functions.
 * <p>Motivation: a need for fast, well distributed, cross-platform
 * hash functions.
 * Most hash functions are defined only in terms of a byte[], and hence
 * underspecified for other data types such as String.
 * </p>
 */
public class Hash {
  /**
   * A Java implementation of hashword from lookup3.c by Bob Jenkins
   * (<a href="http://burtleburtle.net/bob/c/lookup3.c">original source</a>).
   *
   * @param k       the key to hash
   * @param offset  offset of the start of the key
   * @param length  length of the key
   * @param initval initial value to fold into the hash
   * @return the 32 bit hash code
   */
  @SuppressWarnings("fallthrough")
  public static int lookup3(int[] k, int offset, int length, int initval) {
    int a, b, c;
    a = b = c = 0xdeadbeef + (length << 2) + initval;

    int i = offset;
    while (length > 3) {
      a += k[i];
      b += k[i + 1];
      c += k[i + 2];

      // mix(a,b,c)... Java needs "out" parameters!!!
      // Note: recent JVMs (Sun JDK6) turn pairs of shifts (needed to do a rotate)
      // into real x86 rotate instructions.
      {
        a -= c;
        a ^= (c << 4) | (c >>> -4);
        c += b;
        b -= a;
        b ^= (a << 6) | (a >>> -6);
        a += c;
        c -= b;
        c ^= (b << 8) | (b >>> -8);
        b += a;
        a -= c;
        a ^= (c << 16) | (c >>> -16);
        c += b;
        b -= a;
        b ^= (a << 19) | (a >>> -19);
        a += c;
        c -= b;
        c ^= (b << 4) | (b >>> -4);
        b += a;
      }

      length -= 3;
      i += 3;
    }

    switch (length) {
      case 3:
        c += k[i + 2];  // fall through
      case 2:
        b += k[i + 1];  // fall through
      case 1:
        a += k[i + 0];  // fall through
        // final(a,b,c);
      {
        c ^= b;
        c -= (b << 14) | (b >>> -14);
        a ^= c;
        a -= (c << 11) | (c >>> -11);
        b ^= a;
        b -= (a << 25) | (a >>> -25);
        c ^= b;
        c -= (b << 16) | (b >>> -16);
        a ^= c;
        a -= (c << 4) | (c >>> -4);
        b ^= a;
        b -= (a << 14) | (a >>> -14);
        c ^= b;
        c -= (b << 24) | (b >>> -24);
      }
      case 0:
        break;
    }
    return c;
  }


  /**
   * Identical to lookup3, except initval is biased by -(length&lt;&lt;2).
   * This is equivalent to leaving out the length factor in the initial state.
   * {@code lookup3ycs(k,offset,length,initval) ==
   * lookup3(k,offset,length,initval-(length<<2))}
   * and
   * {@code lookup3ycs(k,offset,length,initval+(length<<2)) ==
   * lookup3(k,offset,length,initval)}
   */
  public static int lookup3ycs(int[] k, int offset, int length, int initval) {
    return lookup3(k, offset, length, initval - (length << 2));
  }


  /**
   * <p>The hash value of a character sequence is defined to be the hash of
   * it's unicode code points, according to {@link #lookup3ycs(int[]
   * k, int offset, int length, int initval)}
   * </p>
   * <p>If you know the number of code points in the {@code
   * CharSequence}, you can
   * generate the same hash as the original lookup3
   * via {@code lookup3ycs(s,start,end,initval+(numCodePoints<<2))}
   */
  public static int lookup3ycs(CharSequence s, int start, int end, int
      initval) {
    int a, b, c;
    a = b = c = 0xdeadbeef + initval;
    // only difference from lookup3 is that "+ (length<<2)" is missing
    // since we don't know the number of code points to start with,
    // and don't want to have to pre-scan the string to find out.

    int i = start;
    boolean mixed = true;  // have the 3 state variables been adequately mixed?
    for (; ;) {
      if (i >= end) break;
      mixed = false;
      char ch;
      ch = s.charAt(i++);
      a += Character.isHighSurrogate(ch) && i < end ?
          Character.toCodePoint(ch, s.charAt(i++)) : ch;
      if (i >= end) break;
      ch = s.charAt(i++);
      b += Character.isHighSurrogate(ch) && i < end ?
          Character.toCodePoint(ch, s.charAt(i++)) : ch;
      if (i >= end) break;
      ch = s.charAt(i++);
      c += Character.isHighSurrogate(ch) && i < end ?
          Character.toCodePoint(ch, s.charAt(i++)) : ch;
      if (i >= end) break;

      // mix(a,b,c)... Java needs "out" parameters!!!
      // Note: recent JVMs (Sun JDK6) turn pairs of shifts (needed to do a rotate)
      // into real x86 rotate instructions.
      {
        a -= c;
        a ^= (c << 4) | (c >>> -4);
        c += b;
        b -= a;
        b ^= (a << 6) | (a >>> -6);
        a += c;
        c -= b;
        c ^= (b << 8) | (b >>> -8);
        b += a;
        a -= c;
        a ^= (c << 16) | (c >>> -16);
        c += b;
        b -= a;
        b ^= (a << 19) | (a >>> -19);
        a += c;
        c -= b;
        c ^= (b << 4) | (b >>> -4);
        b += a;
      }
      mixed = true;
    }


    if (!mixed) {
      // final(a,b,c)
      c ^= b;
      c -= (b << 14) | (b >>> -14);
      a ^= c;
      a -= (c << 11) | (c >>> -11);
      b ^= a;
      b -= (a << 25) | (a >>> -25);
      c ^= b;
      c -= (b << 16) | (b >>> -16);
      a ^= c;
      a -= (c << 4) | (c >>> -4);
      b ^= a;
      b -= (a << 14) | (a >>> -14);
      c ^= b;
      c -= (b << 24) | (b >>> -24);
    }

    return c;
  }


  /**
   * <p>This is the 64 bit version of lookup3ycs, corresponding to Bob Jenkin's
   * lookup3 hashlittle2.  It is equivalent to lookup3ycs in that if
   * the high bits
   * of initval==0, then the low bits of the result will be the same
   * as lookup3ycs.
   * </p>
   */
  public static long lookup3ycs64(CharSequence s, int start, int end,
                                  long initval) {
    int a, b, c;
    a = b = c = 0xdeadbeef + (int) initval;
    c += (int) (initval >>> 32);
    // only difference from lookup3 is that "+ (length<<2)" is missing
    // since we don't know the number of code points to start with,
    // and don't want to have to pre-scan the string to find out.

    int i = start;
    boolean mixed = true;  // have the 3 state variables been adequately mixed?
    for (; ;) {
      if (i >= end) break;
      mixed = false;
      char ch;
      ch = s.charAt(i++);
      a += Character.isHighSurrogate(ch) && i < end ?
          Character.toCodePoint(ch, s.charAt(i++)) : ch;
      if (i >= end) break;
      ch = s.charAt(i++);
      b += Character.isHighSurrogate(ch) && i < end ?
          Character.toCodePoint(ch, s.charAt(i++)) : ch;
      if (i >= end) break;
      ch = s.charAt(i++);
      c += Character.isHighSurrogate(ch) && i < end ?
          Character.toCodePoint(ch, s.charAt(i++)) : ch;
      if (i >= end) break;

      // mix(a,b,c)... Java needs "out" parameters!!!
      // Note: recent JVMs (Sun JDK6) turn pairs of shifts (needed to do a rotate)
      // into real x86 rotate instructions.
      {
        a -= c;
        a ^= (c << 4) | (c >>> -4);
        c += b;
        b -= a;
        b ^= (a << 6) | (a >>> -6);
        a += c;
        c -= b;
        c ^= (b << 8) | (b >>> -8);
        b += a;
        a -= c;
        a ^= (c << 16) | (c >>> -16);
        c += b;
        b -= a;
        b ^= (a << 19) | (a >>> -19);
        a += c;
        c -= b;
        c ^= (b << 4) | (b >>> -4);
        b += a;
      }
      mixed = true;
    }


    if (!mixed) {
      // final(a,b,c)
      c ^= b;
      c -= (b << 14) | (b >>> -14);
      a ^= c;
      a -= (c << 11) | (c >>> -11);
      b ^= a;
      b -= (a << 25) | (a >>> -25);
      c ^= b;
      c -= (b << 16) | (b >>> -16);
      a ^= c;
      a -= (c << 4) | (c >>> -4);
      b ^= a;
      b -= (a << 14) | (a >>> -14);
      c ^= b;
      c -= (b << 24) | (b >>> -24);
    }

    return c + (((long) b) << 32);
  }

  /***
   public static void main(String[] args) {
   for (String s : args) {
   int h = lookup3ycs(s,0,s.length(),s.length());
   long h64 = lookup3ycs64(s,0,s.length(),s.length());
   System.out.println("        "+Integer.toHexString(h));
   System.out.println(Long.toHexString(h64));
   if ((int)h64 != h) throw new RuntimeException();
   }
   }
   ***/

}
