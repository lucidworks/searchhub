package com.lucidworks.searchhub.analytics

import scala.collection.mutable

/**
  * Created by jakemannix on 4/29/16.
  */
object GraphUtils {

  /**
    * Finds the adjacency list form of a graph, not caring about orientation
    * @param edges as src->dest pairs
    * @return adjacency list form of the graph
    */
  def buildAdjacencyGraph(edges: List[(String, String)]): Map[String, List[String]] = {
    val outEdges = edges.flatMap(item => Option(item._2).map(rep => (item._1, List(rep))))
    val inEdges = edges.flatMap(item => Option(item._2).map(rep => (rep, List(item._1))))
    val loners = (edges.map(_._1).toSet -- (outEdges.map(_._1) ++ inEdges.map(_._1))).map(_ -> List.empty[String])
    val allEdges = outEdges ++ inEdges ++ loners
    val graph = allEdges.groupBy(_._1).mapValues(_.flatMap(_._2))
    graph
  }

  /**
    * Depth first search to find the connected component of the passed-in vertex
    * @param graph adjacency lists
    * @param components recursive components as they are built
    * @param currentComponent of the current vertex
    * @param vertex to find the component of, via depth-first-search
    */
  def dfs(graph: Map[String, List[String]], components: mutable.Map[String, mutable.ListBuffer[String]],
          currentComponent: mutable.ListBuffer[String],
          vertex: String): Unit = {
    currentComponent += vertex
    components.put(vertex, currentComponent)
    for {
      neighbor <- graph.getOrElse(vertex, List.empty[String])
      if !components.keySet.contains(neighbor)
    } {
      dfs(graph, components, currentComponent, neighbor)
    }
  }

  /**
    * Find the connected components of the graph, as a map which shows which component each vertex is in
    * @param edges as src->dest pairs
    * @return a map of vertex -> list of vertices in its component (including itself)
    */
  def connectedComponents(edges: List[(String, String)]): Map[String, List[String]] = {
    val graph = buildAdjacencyGraph(edges)
    val components = mutable.Map[String, mutable.ListBuffer[String]]()
    graph.keys.foreach { vertex =>
      if (!components.keySet.contains(vertex)) {
        val newComponent = mutable.ListBuffer[String]()
        dfs(graph, components, newComponent, vertex)
      }
    }
    components.mapValues(_.toList).toMap
  }

}
