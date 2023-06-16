<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:fedora="http://fedora.info/definitions/v4/repository#"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.w3.org/1999/02/22-rdf-syntax-ns# http://www.openarchives.org/OAI/2.0/rdf.xsd">
  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <rdf:RDF xsi:schemaLocation="http://www.w3.org/1999/02/22-rdf-syntax-ns# http://www.openarchives.org/OAI/2.0/rdf.xsd">
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates select="rdf:RDF/rdf:Description"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- skip the fedora:writable element -->
  <xsl:template match="fedora:writable"/>
</xsl:stylesheet>
