# -*- coding: utf-8 -*-

# Zope3 imports
from zope.component import getUtility
from Acquisition import aq_inner

# Product imports
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

#Plone imports
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry


#Libs imports


# lx.demanda imports
from lx.demanda.interfaces.contents import IDemanda
from lx.demanda.interfaces.interfaces import ICatalogoServicoPrefsForm


class ListaDemandaOSView(BrowserView):
    """ view 
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def settings(self):
        if 'form.action.ordemServico' in self.request.form:
            if self.validateOrdemServico():
                return self.getDemandas()

    @memoize
    def validateOrdemServico(self):
        """Validação
        """
        context = aq_inner(self.context)
        utils = getToolByName(context, 'plone_utils')
        ordemServico = self.request.get('ordemServico', None)
        if (ordemServico == ' ') or (ordemServico == None):
            self.errors['ordem_servico'] = "O campo é obrigatório."
        # Check for errors
        if self.errors:
            utils.addPortalMessage("Corrija os erros.", type='error')
            return False
        else:
            return True


    @memoize
    def getDemandas(self):
        """
        """
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = '/'.join(self.context.getPhysicalPath())
        ordemServico = self.request.get('ordemServico', None)
        if (ordemServico == None):
            os = self.getOS()
            if os:
                ordemServico = os[0]
        if (ordemServico != None) and (ordemServico != ' '):
            demandas = catalog(object_provides=IDemanda.__identifier__,
                               path=path_demandas,
                               ordem_servico=ordemServico,
                               sort_on='chamado',
                               sort_order='reverse',)
            return demandas

    @memoize
    def getTotalHST(self):
        """
        """
        demandas = self.getDemandas()
        quantidades = []
        for i in demandas:
            totalAt = i.quantHST
            quantidades.append(totalAt)
        total = sum(quantidades)
        return total

    @memoize
    def getOS(self):
        # registry = getUtility(IRegistry)
        # settings = registry.forInterface(ICatalogoServicoPrefsForm)
        ordens_servicos = tuple()
        try:
            # ordens_servicos = ordens_servicos + settings.ordem_servico
            ordens_servicos = ordens_servicos + self.context.aq_parent.lista_os
        except:
            ordens_servicos = ordens_servicos
        return ordens_servicos

    @memoize
    def requestOS(self):
        ordemServico = self.request.get('ordemServico', None)
        if (ordemServico == None):
            os = self.getOS()
            if os:
                ordemServico = os[0]
        type_var = type(ordemServico)
        texto = ''
        parametro = 'ordemServico:list='
        if type_var == list:
            for i in ordemServico:
                texto += parametro + i + '&'
        else:
            texto += parametro + ordemServico
        return texto