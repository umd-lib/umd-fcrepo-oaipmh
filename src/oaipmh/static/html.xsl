<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:oai="http://www.openarchives.org/OAI/2.0/">

  <xsl:variable name="baseURL" select="/oai:OAI-PMH/oai:request"/>

  <xsl:template match="/oai:OAI-PMH">
    <html>
      <head>
        <title>OAI-PMH Service</title>
        <link rel="stylesheet" type="text/css" href="{$baseURL}/../static/oai.css"/>
      </head>
      <body>
        <div>
          <a href="{$baseURL}?verb=Identify">Identify</a> |
          <a href="{$baseURL}?verb=ListMetadataFormats">ListMetadataFormats</a> |
          <a href="{$baseURL}?verb=ListSets">ListSets</a>
        </div>
        <xsl:apply-templates select="oai:error|oai:Identify|oai:ListMetadataFormats|oai:ListIdentifiers|oai:ListRecords|oai:ListSets|oai:GetRecord"/>
        <xsl:apply-templates select="oai:responseDate"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="oai:request">
    <dl>
      <xsl:for-each select="@*">
        <dt><xsl:value-of select="local-name()"/></dt>
        <dd><xsl:value-of select="."/></dd>
      </xsl:for-each>
      <dt>baseURL</dt>
      <dd><xsl:value-of select="."/></dd>
    </dl>
  </xsl:template>

  <xsl:template match="oai:error">
    <h1>Error</h1>
    <dl>
      <dt>code</dt>
      <dd><xsl:value-of select="@code"/></dd>
      <dt>message</dt>
      <dd><xsl:value-of select="."/></dd>
    </dl>
  </xsl:template>

  <xsl:template match="oai:Identify">
    <h1>Identify</h1>
    <h2>Request</h2>
    <xsl:apply-templates select="../oai:request"/>
    <h2>Response</h2>
    <div class="response-date">
      <xsl:value-of select="/oai:OAI-PMH/oai:responseDate"/>
    </div>
    <dl>
      <xsl:for-each select="*">
        <dt><xsl:value-of select="local-name()"/></dt>
        <dd><xsl:value-of select="."/></dd>
      </xsl:for-each>
    </dl>
  </xsl:template>

  <xsl:template match="oai:ListMetadataFormats">
    <h1>ListMetadataFormats</h1>
    <h2>Request</h2>
    <xsl:apply-templates select="../oai:request"/>
    <h2>Response</h2>
    <xsl:apply-templates select="oai:metadataFormat"/>
  </xsl:template>

  <xsl:template match="oai:ListIdentifiers">
    <h1>ListIdentifiers</h1>
    <h2>Request</h2>
    <xsl:apply-templates select="../oai:request"/>
    <h2>Response</h2>
    <xsl:call-template name="pagination"/>
    <ol start="{number(oai:resumptionToken/@cursor) + 1}">
      <xsl:for-each select="oai:header">
        <li>
          <xsl:apply-templates select="."/>
        </li>
      </xsl:for-each>
    </ol>
    <xsl:apply-templates select="oai:resumptionToken"/>
  </xsl:template>

  <xsl:template match="oai:ListRecords">
    <h1>ListRecords</h1>
    <h2>Request</h2>
    <xsl:apply-templates select="../oai:request"/>
    <h2>Response</h2>
    <xsl:call-template name="pagination"/>
    <ol start="{number(oai:resumptionToken/@cursor) + 1}">
      <xsl:for-each select="oai:record">
        <li>
          <xsl:apply-templates select="."/>
        </li>
      </xsl:for-each>
    </ol>
    <xsl:apply-templates select="oai:resumptionToken"/>
  </xsl:template>

  <xsl:template match="oai:ListSets">
    <h1>ListSets</h1>
    <h2>Request</h2>
    <xsl:apply-templates select="../oai:request"/>
    <h2>Response</h2>
    <xsl:call-template name="pagination"/>
    <ol start="{number(oai:resumptionToken/@cursor) + 1}">
      <xsl:for-each select="oai:set">
        <li>
          <xsl:apply-templates select="."/>
        </li>
      </xsl:for-each>
    </ol>
    <xsl:apply-templates select="oai:resumptionToken"/>
  </xsl:template>

  <xsl:template match="oai:GetRecord">
    <h1>GetRecord</h1>
    <h2>Request</h2>
    <xsl:apply-templates select="../oai:request"/>
    <h2>Response</h2>
    <xsl:apply-templates select="oai:record"/>
  </xsl:template>

  <xsl:template match="oai:metadata">
    <h3>Metadata</h3>
    <pre><xsl:apply-templates mode="escape"/></pre>
  </xsl:template>

  <xsl:template match="oai:metadataFormat">
    <h3><xsl:value-of select="oai:metadataPrefix"/></h3>
    <dl>
      <dt>prefix</dt>
      <dd>
        <form method="get" action="{$baseURL}">
          <strong>
            <xsl:value-of select="oai:metadataPrefix"/>
          </strong>
          <input type="hidden" name="metadataPrefix" value="{oai:metadataPrefix}"/>
          <div class="buttons">
            <button name="verb" value="ListIdentifiers">ListIdentifiers</button>
            <button name="verb" value="ListRecords">ListRecords</button>
          </div>
        </form>
      </dd>
      <dt>namespace</dt>
      <dd>
        <a href="{oai:metadataNamespace}">
          <xsl:value-of select="oai:metadataNamespace"/>
        </a>
      </dd>
      <dt>schema</dt>
      <dd>
        <a href="{oai:schema}">
          <xsl:value-of select="oai:schema"/>
        </a>
      </dd>
    </dl>
  </xsl:template>

  <xsl:template match="oai:header">
    <dl>
      <xsl:apply-templates select="oai:identifier"/>
      <xsl:apply-templates select="oai:datestamp"/>
      <xsl:apply-templates select="oai:setSpec"/>
    </dl>
  </xsl:template>

  <xsl:template match="oai:identifier">
    <dt>identifier</dt>
    <dd>
      <xsl:variable name="escaped-identifier">
        <xsl:call-template name="uri-escape">
          <xsl:with-param name="text" select="."/>
        </xsl:call-template>
      </xsl:variable>
      <form method="get" action="{$baseURL}">
        <strong>
          <xsl:value-of select="."/>
        </strong>
        <input type="hidden" name="verb" value="GetRecord"/>
        <input type="hidden" name="identifier" value="{.}"/>
        <div class="buttons">
          <button name="metadataPrefix" value="oai_dc">oai_dc</button>
          <button name="metadataPrefix" value="rdf">rdf</button>
        </div>
      </form>
    </dd>
  </xsl:template>

  <xsl:template match="oai:datestamp">
    <dt>datestamp</dt>
    <dd><xsl:value-of select="."/></dd>
  </xsl:template>

  <xsl:template match="oai:setSpec">
    <dt>setSpec</dt>
    <dd><xsl:value-of select="."/></dd>
  </xsl:template>

  <xsl:template match="oai:record">
    <xsl:apply-templates select="oai:header"/>
    <xsl:apply-templates select="oai:metadata"/>
  </xsl:template>

  <xsl:template match="oai:set">
    <h3><xsl:value-of select="oai:setName"/></h3>
    <dl>
      <dt>setSpec</dt>
      <dd>
        <form method="get" action="{$baseURL}">
          <xsl:value-of select="oai:setSpec"/>
          <input type="hidden" name="set" value="{oai:setSpec}"/>
          <div class="buttons">
            <select name="metadataPrefix">
              <option>oai_dc</option>
              <option>rdf</option>
            </select>
            <button name="verb" value="ListIdentifiers">ListIdentifiers</button>
            <button name="verb" value="ListRecords">ListRecords</button>
          </div>
        </form>
      </dd>
      <dt>setName</dt>
      <dd><xsl:value-of select="oai:setName"/></dd>
    </dl>
  </xsl:template>

  <xsl:template match="oai:resumptionToken">
    <xsl:if test=". != ''">
      <div>
        <form method="get" action="{$baseURL}">
          <input type="hidden" name="verb">
            <xsl:attribute name="value">
              <xsl:value-of select="local-name(/oai:OAI-PMH/oai:request/following-sibling::*)"/>
            </xsl:attribute>
          </input>
          <input type="hidden" name="resumptionToken" value="{.}"/>
          <button>More</button>
        </form>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="oai:responseDate">
    <div class="response-date">
      Response sent at <xsl:value-of select="."/>
    </div>
  </xsl:template>

  <!-- source: https://w3toppers.com/converting-xml-to-escaped-text-in-xslt/ -->
  <xsl:template match="*" mode="escape">
    <!-- Begin opening tag -->
    <span class="element">
      <xsl:text>&lt;</xsl:text>
      <xsl:value-of select="name()"/>
    </span>

    <!-- Namespaces -->
    <xsl:for-each select="namespace::*">
      <xsl:text> xmlns</xsl:text>
      <xsl:if test="name() != ''">
        <xsl:text>:</xsl:text>
        <xsl:value-of select="name()"/>
      </xsl:if>
      <xsl:text>='</xsl:text>
      <xsl:call-template name="escape-xml">
        <xsl:with-param name="text" select="."/>
      </xsl:call-template>
      <xsl:text>'</xsl:text>
    </xsl:for-each>

    <!-- Attributes -->
    <xsl:for-each select="@*">
      <xsl:text> </xsl:text>
      <span class="attribute-name">
        <xsl:value-of select="name()"/>
      </span>
      <xsl:text>=</xsl:text>
      <span class="attribute-value">
        <xsl:text>"</xsl:text>
        <xsl:call-template name="escape-xml">
          <xsl:with-param name="text" select="."/>
        </xsl:call-template>
        <xsl:text>"</xsl:text>
      </span>
    </xsl:for-each>

    <!-- End opening tag -->
    <span class="element">
      <xsl:text>&gt;</xsl:text>
    </span>

    <!-- Content (child elements, text nodes, and PIs) -->
    <xsl:apply-templates mode="escape"/>

    <!-- Closing tag -->
    <span class="element">
      <xsl:text>&lt;/</xsl:text>
      <xsl:value-of select="name()"/>
      <xsl:text>&gt;</xsl:text>
    </span>
  </xsl:template>

  <xsl:template match="text()" mode="escape">
    <xsl:call-template name="escape-xml">
      <xsl:with-param name="text" select="."/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="processing-instruction()" mode="escape">
    <xsl:text>&lt;?</xsl:text>
    <xsl:value-of select="name()"/>
    <xsl:text> </xsl:text>
    <xsl:call-template name="escape-xml">
      <xsl:with-param name="text" select="."/>
    </xsl:call-template>
    <xsl:text>?&gt;</xsl:text>
  </xsl:template>

  <xsl:template name="pagination">
    <xsl:variable name="first">
      <xsl:choose>
        <xsl:when test="oai:resumptionToken">
          <xsl:value-of select="number(oai:resumptionToken/@cursor) + 1"/>
        </xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="last" select="$first + count(oai:header|oai:record|oai:set) - 1"/>
    <xsl:variable name="total">
      <xsl:choose>
        <xsl:when test="oai:resumptionToken">
          <xsl:value-of select="number(oai:resumptionToken/@completeListSize)"/>
        </xsl:when>
        <xsl:otherwise><xsl:value-of select="$last"/></xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <div>
      Results <xsl:value-of select="$first"/>–<xsl:value-of select="$last"/> of <xsl:value-of select="$total"/>
    </div>
  </xsl:template>

  <xsl:template name="escape-xml">
    <xsl:param name="text"/>
    <xsl:if test="$text != ''">
      <xsl:variable name="head" select="substring($text, 1, 1)"/>
      <xsl:variable name="tail" select="substring($text, 2)"/>
      <xsl:choose>
        <xsl:when test="$head = '&amp;'">&amp;amp;</xsl:when>
        <xsl:when test="$head = '&lt;'">&amp;lt;</xsl:when>
        <xsl:when test="$head = '&gt;'">&amp;gt;</xsl:when>
        <xsl:when test="$head = '&quot;'">&amp;quot;</xsl:when>
        <xsl:when test="$head = &quot;&apos;&quot;">&amp;apos;</xsl:when>
        <xsl:otherwise><xsl:value-of select="$head"/></xsl:otherwise>
      </xsl:choose>
      <xsl:call-template name="escape-xml">
        <xsl:with-param name="text" select="$tail"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template name="uri-escape">
    <xsl:param name="text"/>
    <xsl:if test="$text != ''">
      <xsl:variable name="head" select="substring($text, 1, 1)"/>
      <xsl:variable name="tail" select="substring($text, 2)"/>
      <xsl:choose>
        <xsl:when test="$head = ':'">%3A</xsl:when>
        <xsl:when test="$head = '/'">%2F</xsl:when>
        <xsl:when test="$head = '%'">%25</xsl:when>
        <xsl:otherwise><xsl:value-of select="$head"/></xsl:otherwise>
      </xsl:choose>
      <xsl:call-template name="uri-escape">
        <xsl:with-param name="text" select="$tail"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>
