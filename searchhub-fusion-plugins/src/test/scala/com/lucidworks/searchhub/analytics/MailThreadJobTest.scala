package com.lucidworks.searchhub.analytics

import org.apache.spark.sql.SQLContext
import org.apache.spark.{SparkContext, SparkConf}
import org.scalatest.FunSuite

case class DummyMailMessage(id: String, in_reply_to: String, threadId: String, subject_simple: String)

class MailThreadJobTest extends FunSuite {
  val rawMsgs = List(
    DummyMailMessage("<1204067533.21932.4.camel@cartman>", null, "<1204067533.21932.4.camel@cartman>", "documentation"),
    DummyMailMessage("<1204134685.723.9.camel@cartman>", "<510143ac0802261529w49eb0d3ekab6a1a0da3eb740e@mail.gmail.com>", "<1204067533.21932.4.camel@cartman>", "documentation"),
    DummyMailMessage("<510143ac0802261529w49eb0d3ekab6a1a0da3eb740e@mail.gmail.com>", "<1204067533.21932.4.camel@cartman>", "<1204067533.21932.4.camel@cartman>", "documentation"),
    DummyMailMessage("<AANLkTi=4trKTVvsdAMxsSM5rpLVxLz3ecshL_ySNsr7+@mail.gmail.com>", "<C865F300.18BD3%Chris.A.Mattmann@jpl.nasa.gov>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTiks_3itLShGop2th5IAsiMxTfLru7RG5g35ksU9@mail.gmail.com>", "<AANLkTimM-O0T9wUdGqulJEG-bslTUGp5faEP0nq8HveB@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTimM-O0T9wUdGqulJEG-bslTUGp5faEP0nq8HveB@mail.gmail.com>", "<AANLkTinmtjGPb3yMgIojRe_BFR_h9tv1FW-NmV3FM0kR@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTimoxJ3FN8a877Brwt6bZtN1N3VIDPqEGrasMpLw@mail.gmail.com>", "<alpine.DEB.1.10.1007121627320.2517@urchin.earth.li>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTimxsL6p8fL2x1syxVNRknDl72yrhO3KyHjSeSaB@mail.gmail.com>", "<AANLkTimM-O0T9wUdGqulJEG-bslTUGp5faEP0nq8HveB@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTimyEf_NQZlacpzEEFguwmX2dV4L7-NXnb1rg3D8@mail.gmail.com>", "<AANLkTiks_3itLShGop2th5IAsiMxTfLru7RG5g35ksU9@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", null, "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTinmtjGPb3yMgIojRe_BFR_h9tv1FW-NmV3FM0kR@mail.gmail.com>", "<alpine.DEB.1.10.1007121627320.2517@urchin.earth.li>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<AANLkTinzdvkBRsj43rDVZppQOoIMznIY5HJ9TvPvZxPc@mail.gmail.com>", "<AANLkTimyEf_NQZlacpzEEFguwmX2dV4L7-NXnb1rg3D8@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<C865F300.18BD3%Chris.A.Mattmann@jpl.nasa.gov>", "<AANLkTinzdvkBRsj43rDVZppQOoIMznIY5HJ9TvPvZxPc@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<C87C7740.1A362%Chris.A.Mattmann@jpl.nasa.gov>", "<AANLkTi=4trKTVvsdAMxsSM5rpLVxLz3ecshL_ySNsr7+@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<alpine.DEB.1.10.1007121627320.2517@urchin.earth.li>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<alpine.DEB.1.10.1007121811030.2517@urchin.earth.li>", "<AANLkTimoxJ3FN8a877Brwt6bZtN1N3VIDPqEGrasMpLw@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes"),
    DummyMailMessage("<alpine.DEB.1.10.1007151226020.2517@urchin.earth.li>", "<AANLkTinmtjGPb3yMgIojRe_BFR_h9tv1FW-NmV3FM0kR@mail.gmail.com>", "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>", "packages and attributes")
  )

  test("mail threading on two thread groups") {
    val sparkConfig = new SparkConf().set("spark.ui.enabled", "false")
    val sc = new SparkContext("local", "test", sparkConfig)
    val sqlContext = new SQLContext(sc)

    // remove the threadIds which are in the above data set
    val msgRdd = sc.parallelize(rawMsgs.map(_.copy(threadId = null)))
    val msgDF = sqlContext.createDataFrame(msgRdd)

    assert(msgDF.count() == rawMsgs.size, "Sanity check on size has failed!")
    val withThreads = MailThreadJob.createThreadGroups(msgDF, alwaysOverride = true)
    assert(withThreads.count() == rawMsgs.size, "Threaded messages should also be same size")
    assert(withThreads.filter(withThreads("threadId").isNull).count() == 0, "Not everyone accounted for!")
    val documentationThreadIds = withThreads.filter("subject_simple = 'documentation'").select("threadId").collect()
    assert(documentationThreadIds.size == 3)
    assert(documentationThreadIds.toSet.size == 1)
    assert(documentationThreadIds.head.get(0).toString == "<1204067533.21932.4.camel@cartman>")

    val pkgsAndAttrsThreadIds = withThreads.filter("subject_simple = 'packages and attributes'").select("threadId").collect()
    assert(pkgsAndAttrsThreadIds.size == 14)
    assert(pkgsAndAttrsThreadIds.toSet.size == 1)
    assert(pkgsAndAttrsThreadIds.head.get(0).toString == "<AANLkTin648hqqHEL0PQNyW0QsC5oCLvLkmP53MB5bt2I@mail.gmail.com>")
  }
}
